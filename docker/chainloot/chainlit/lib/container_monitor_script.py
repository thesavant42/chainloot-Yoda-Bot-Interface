#!/usr/bin/env python3
"""
Container Monitor Script
Fetches Docker container data via HTTP API and publishes to MQTT
"""

import requests
import json
import paho.mqtt.publish as publish
import time
import sys

def fetch_containers():
    """Fetch all containers data from Docker API"""
    try:
        url = "http://host.docker.internal:2375/v1.43/containers/json"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Docker API error: {response.status_code}")
            return None
    except Exception as e:
        print(f"Failed to fetch containers data: {e}")
        return None

def publish_container_data(container_data):
    """Publish container data to MQTT"""
    try:
        # Extract container name (remove leading slash)
        names = container_data.get("Names", [])
        if not names:
            return

        container_name = names[0].lstrip('/')

        # Publish the complete container JSON data
        topic = f"/chainloot/system/containers/{container_name}"
        payload = json.dumps(container_data)

        publish.single(
            topic=topic,
            payload=payload,
            hostname="192.168.1.98",
            port=1883,
            retain=True,
            qos=1
        )

        print(f"Published data for container: {container_name}")

    except Exception as e:
        print(f"Failed to publish container data: {e}")

def main():
    """Main monitoring function"""
    print("Starting container monitoring...")

    # Fetch container data
    containers = fetch_containers()
    if not containers:
        print("No container data received")
        sys.exit(1)

    # Publish data for each container
    for container in containers:
        publish_container_data(container)

    print(f"Monitoring complete. Published data for {len(containers)} containers.")

if __name__ == "__main__":
    main()