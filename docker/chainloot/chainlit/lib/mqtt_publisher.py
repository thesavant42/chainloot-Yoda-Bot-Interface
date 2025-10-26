import paho.mqtt.client as mqtt
import json
import time
import os
from typing import Dict, Any

class MQTTPublisher:
    def __init__(self, broker_host: str = "mosquitto", broker_port: int = 1883, username: str = "yoda", password: str = "yoda"):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.username = username
        self.password = password
        self.client = None
        self.connected = False
        
    def connect(self):
        """Connect to the MQTT broker"""
        if self.client is None:
            self.client = mqtt.Client(
                protocol=mqtt.MQTTv5,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )
            self.client.username_pw_set(self.username, self.password)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            # Wait for connection to establish
            timeout = 5  # seconds
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            if not self.connected:
                print("MQTT Connection timeout")
                self.client.loop_stop()
                self.client = None
        except Exception as e:
            print(f"MQTT Connection failed: {e}")
            self.connected = False
            
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print("MQTT Connected successfully")
        else:
            self.connected = False
            print(f"MQTT Connection failed with code {rc}")
            
    def _on_disconnect(self, client, userdata, rc, properties=None):
        self.connected = False
        print("MQTT Disconnected")
        
    def publish_emotion(self, persona: str, emotion_data: Dict[str, Any], expiry_interval: int = 300):
        """Publish emotion data for a persona"""
        if not self.connected:
            self.connect()
            
        if not self.connected:
            print("MQTT not connected, skipping publish")
            return
            
        topic = f"/chainloot/persona/{persona}/feelings"
        
        payload = {
            "timestamp": int(time.time()),
            "dominant_emotion": emotion_data.get("dominant_emotion", "neutral"),
            "weights": emotion_data.get("weights", {}),
            "dominant_score": emotion_data.get("dominant_score", 0.0)
        }
        
        try:
            # Set MQTT v5.0 properties for expiry
            properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = expiry_interval
            
            result = self.client.publish(
                topic, 
                json.dumps(payload), 
                qos=1, 
                retain=True,
                properties=properties
            )
            result.wait_for_publish()
            print(f"Published emotion to {topic}: {payload['dominant_emotion']} (expires in {expiry_interval}s)")
        except Exception as e:
            print(f"Failed to publish MQTT message: {e}")
            
    def publish_status(self, persona: str, status: str, expiry_interval: int = 60):
        """Publish status update (online, idle, etc.)"""
        if not self.connected:
            self.connect()
            
        if not self.connected:
            print("MQTT not connected, skipping status publish")
            return
            
        topic = f"/chainloot/persona/{persona}/status"
        
        payload = {
            "timestamp": int(time.time()),
            "status": status
        }
        
        try:
            # Set MQTT v5.0 properties for expiry
            properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = expiry_interval
            
            result = self.client.publish(
                topic, 
                json.dumps(payload), 
                qos=1, 
                retain=True,
                properties=properties
            )
            result.wait_for_publish()
            print(f"Published status to {topic}: {status} (expires in {expiry_interval}s)")
        except Exception as e:
            print(f"Failed to publish MQTT status: {e}")
            
    def publish_resource_usage(self, resource_data: Dict[str, Any], container: str = "system", expiry_interval: int = 300):
        """Publish system or container resource usage data"""
        if not self.connected:
            self.connect()
            
        if not self.connected:
            print("MQTT not connected, skipping resource publish")
            return
            
        topic = f"/chainloot/system/{container}/resources"
        
        # Handle different data formats (system vs container)
        if container == "system":
            # System-wide resources
            payload = {
                "timestamp": resource_data.get("timestamp", int(time.time())),
                "cpu_percent": resource_data.get("cpu_percent"),
                "memory": resource_data.get("memory"),
                "gpu": resource_data.get("gpu"),
                "disk": resource_data.get("disk")
            }
        else:
            # Container-specific resources
            payload = {
                "timestamp": resource_data.get("timestamp", int(time.time())),
                "cpu_percent": resource_data.get("cpu_percent"),
                "memory_usage": resource_data.get("memory_usage"),
                "memory_limit": resource_data.get("memory_limit"),
                "memory_percent": resource_data.get("memory_percent"),
                "status": resource_data.get("status")
            }
        
        try:
            # Set MQTT v5.0 properties for expiry
            properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = expiry_interval
            
            result = self.client.publish(
                topic, 
                json.dumps(payload), 
                qos=1, 
                retain=True,
                properties=properties
            )
            result.wait_for_publish()
            
            if container == "system":
                print(f"Published system resource usage to {topic}: CPU {payload['cpu_percent']}%, Memory {payload['memory']['percent']}%")
            else:
                print(f"Published container resource usage to {topic}: CPU {payload['cpu_percent']}%, Memory {payload['memory_percent']}%")
        except Exception as e:
            print(f"Failed to publish resource data: {e}")
            
    def publish_service_status(self, service_data: Dict[str, Any], service_name: str, expiry_interval: int = 300):
        """Publish service availability status"""
        if not self.connected:
            self.connect()
            
        if not self.connected:
            print("MQTT not connected, skipping service status publish")
            return
            
        topic = f"/chainloot/system/{service_name}/services"
        
        payload = {
            "timestamp": service_data.get("timestamp", int(time.time())),
            "service": service_data
        }
        
        try:
            # Set MQTT v5.0 properties for expiry
            properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
            properties.MessageExpiryInterval = expiry_interval
            
            result = self.client.publish(
                topic, 
                json.dumps(payload), 
                qos=1, 
                retain=True,
                properties=properties
            )
            result.wait_for_publish()
            status = "available" if service_data.get("available", False) else "unavailable"
            print(f"Published service status to {topic}: {service_name} is {status}")
        except Exception as e:
            print(f"Failed to publish service status: {e}")
            
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False

# Global instance
_mqtt_publisher = None

def get_mqtt_publisher() -> MQTTPublisher:
    """Get or create the global MQTT publisher instance"""
    global _mqtt_publisher
    if _mqtt_publisher is None:
        # Use environment variables if available, otherwise defaults
        broker_host = os.getenv("MQTT_BROKER_HOST", "mosquitto")
        broker_port = int(os.getenv("MQTT_BROKER_PORT", "1883"))
        username = os.getenv("MQTT_USERNAME", "yoda")
        password = os.getenv("MQTT_PASSWORD", "yoda")
        
        _mqtt_publisher = MQTTPublisher(broker_host, broker_port, username, password)
    return _mqtt_publisher