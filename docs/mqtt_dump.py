#!/usr/bin/env python3
"""
MQTT Topic Dumper
Subscribes to /chainloot/system/# and prints all received messages for inspection.
Run this to see all available topics and payloads for badging decisions.
"""

import paho.mqtt.client as mqtt
import json
import time

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("/chainloot/system/#")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        # Try to parse as JSON for pretty printing
        try:
            parsed = json.loads(payload)
            pretty_payload = json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            pretty_payload = payload

        print(f"\nTopic: {msg.topic}")
        print(f"Payload: {pretty_payload}")
        print("-" * 50)
    except Exception as e:
        print(f"Error processing message on {msg.topic}: {e}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to broker
    client.connect("192.168.1.98", 1883, 60)

    print("MQTT Topic Dumper starting...")
    print("Subscribing to /chainloot/system/#")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        client.disconnect()

if __name__ == "__main__":
    main()