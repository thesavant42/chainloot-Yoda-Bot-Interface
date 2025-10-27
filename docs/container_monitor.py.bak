"""
Lightweight Container Monitor for Chainlit
Fetches Docker container data via HTTP API and publishes to MQTT
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional
from lib.mqtt_publisher import get_mqtt_publisher
from lib.feels_classifier import classify_sentiment


class ContainerMonitor:
    """Lightweight container monitor that fetches Docker data and publishes to MQTT"""

    def __init__(self):
        self.mqtt_publisher = get_mqtt_publisher()
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        self.docker_api_url = "http://host.docker.internal:2375/v1.43/containers/json"

    async def fetch_containers_data(self) -> Optional[list]:
        """Fetch all containers data from Docker API"""
        try:
            timeout = aiohttp.ClientTimeout(total=10.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.docker_api_url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"Docker API error: {response.status}")
                        return None
        except Exception as e:
            print(f"Failed to fetch containers data: {e}")
            return None

    def organize_container_data(self, containers: list) -> Dict[str, Any]:
        """Organize ALL container data from Docker API for MQTT publishing"""
        organized = {
            "containers": {},
            "services": {}
        }

        # Map container names to service names (from docker-compose.yml)
        service_mapping = {
            "chainloot-postgres-1": "postgres",
            "chainloot-localstack-1": "localstack",
            "chainloot-tts-webui-1": "tts_webui",
            "chainloot-chainlit-1": "chainlit",
            "chainloot-ollama-1": "ollama",
            "chainloot-mosquitto-1": "mosquitto"
        }

        for container in containers:
            names = container.get("Names", [])
            if not names:
                continue

            # Remove leading slash from container name
            container_name = names[0].lstrip('/')
            service_name = service_mapping.get(container_name)

            # Include ALL data from Docker API response
            organized["containers"][container_name] = container.copy()

            # Add timestamp for monitoring
            organized["containers"][container_name]["timestamp"] = int(time.time())

            # Create service data with ALL container information
            if service_name:
                organized["services"][service_name] = container.copy()
                organized["services"][service_name]["timestamp"] = int(time.time())
                organized["services"][service_name]["service_name"] = service_name

        return organized

    def publish_container_data(self, data: Dict[str, Any]):
        """Publish ALL container data to nested MQTT topics"""
        try:
            # Publish container data with full nested structure
            for container_name, container_data in data["containers"].items():
                self._publish_nested_data(f"/chainloot/system/containers/{container_name}", container_data)

            # Publish service data with full nested structure
            for service_name, service_data in data["services"].items():
                self._publish_nested_data(f"/chainloot/system/services/{service_name}", service_data)

            print(f"Published complete data for {len(data['containers'])} containers and {len(data['services'])} services")

        except Exception as e:
            print(f"Failed to publish container data: {e}")

    def _publish_nested_data(self, base_topic: str, data: Any, max_depth: int = 5):
        """Recursively publish nested data to MQTT topics"""
        if max_depth <= 0:
            return

        if isinstance(data, dict):
            # Publish the entire object as JSON to the base topic
            try:
                self.mqtt_publisher.client.publish(
                    base_topic,
                    json.dumps(data),
                    qos=1,
                    retain=True
                )
            except:
                pass  # Skip if MQTT not connected

            # Then publish each nested field
            for key, value in data.items():
                topic = f"{base_topic}/{key}"
                if isinstance(value, (dict, list)):
                    self._publish_nested_data(topic, value, max_depth - 1)
                else:
                    # Publish primitive values
                    try:
                        self.mqtt_publisher.client.publish(
                            topic,
                            str(value),
                            qos=1,
                            retain=True
                        )
                    except:
                        pass  # Skip if MQTT not connected

        elif isinstance(data, list):
            # Publish the entire array as JSON
            try:
                self.mqtt_publisher.client.publish(
                    base_topic,
                    json.dumps(data),
                    qos=1,
                    retain=True
                )
            except:
                pass

            # Publish each array element
            for i, item in enumerate(data):
                topic = f"{base_topic}/{i}"
                if isinstance(item, (dict, list)):
                    self._publish_nested_data(topic, item, max_depth - 1)
                else:
                    try:
                        self.mqtt_publisher.client.publish(
                            topic,
                            str(item),
                            qos=1,
                            retain=True
                        )
                    except:
                        pass

    async def monitoring_loop(self, interval: int = 30):
        """Main monitoring loop"""
        print(f"Starting lightweight container monitoring (interval: {interval}s)")

        while self.monitoring_active:
            try:
                # Fetch raw container data
                raw_data = await self.fetch_containers_data()
                if raw_data:
                    # Organize data for MQTT
                    organized_data = self.organize_container_data(raw_data)
                    # Publish to MQTT
                    self.publish_container_data(organized_data)
                else:
                    print("No container data received")

            except Exception as e:
                print(f"Monitoring loop error: {e}")

            # Wait for next interval
            await asyncio.sleep(interval)

    def start_monitoring(self, interval: int = 30):
        """Start the monitoring task"""
        if self.monitoring_active:
            print("Container monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self.monitoring_loop(interval))
        print("Container monitoring started")

    def stop_monitoring(self):
        """Stop the monitoring task"""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            print("Container monitoring stopped")


# Global instance
_monitor = None

def get_container_monitor() -> ContainerMonitor:
    """Get the global container monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = ContainerMonitor()
    return _monitor


# Emotion classification functions (preserved from original)
def classify_text_emotion(text: str) -> Dict[str, Any]:
    """Classify emotion in text and return MQTT-ready data"""
    result = classify_sentiment(text)
    if "error" not in result:
        return {
            "text": text[:100],  # Truncate for MQTT
            "dominant_emotion": result.get("dominant_emotion", "neutral"),
            "dominant_score": result.get("dominant_score", 0.0),
            "weights": result.get("weights", {}),
            "timestamp": int(time.time())
        }
    return {"error": result.get("error", "Unknown error")}

def publish_emotion_data(text: str, persona: str):
    """Analyze text emotion and publish to MQTT"""
    emotion_data = classify_text_emotion(text)
    monitor = get_container_monitor()
    monitor.mqtt_publisher.publish_emotion(persona.lower(), emotion_data, expiry_interval=300)
    return emotion_data