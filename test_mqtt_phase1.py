#!/usr/bin/env python3
"""
Phase 1 MQTT Testing Script - Chainloot Yoda Bot Interface
Tests MQTT 5.0 implementation with message expiry intervals.

This script can be run independently to verify:
1. MQTT broker connectivity with authentication
2. Message publishing with expiry intervals
3. Retained message cleanup

Usage:
    python test_mqtt_phase1.py

Environment Variables (set these before running):
    MQTT_BROKER - MQTT broker hostname/IP (default: localhost)
    MQTT_PORT - MQTT broker port (default: 1883)
    MQTT_USERNAME - MQTT username (default: yoda)
    MQTT_PASSWORD - MQTT password (required for authentication)
"""

import os
import sys
import time
import json
import paho.mqtt.client as mqtt
from typing import Dict, Any

def test_mqtt_connectivity():
    """Test basic MQTT connectivity and authentication"""
    print("=== Testing MQTT Connectivity ===")

    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME", "yoda")
    password = os.getenv("MQTT_PASSWORD", "")

    if not password:
        print("❌ ERROR: MQTT_PASSWORD environment variable not set")
        return False

    print(f"Connecting to {broker}:{port} as {username}")

    client = mqtt.Client(
        client_id="test-client-phase1",
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    client.username_pw_set(username, password)

    connected = False
    def on_connect(client, userdata, flags, reason_code, properties):
        nonlocal connected
        if reason_code == 0:
            print("✅ Connected successfully")
            connected = True
        else:
            print(f"❌ Connection failed: {reason_code}")

    client.on_connect = on_connect

    try:
        client.connect(broker, port, 10)
        client.loop_start()
        time.sleep(2)  # Wait for connection
        client.loop_stop()
        client.disconnect()
        return connected
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_message_expiry():
    """Test message publishing with expiry intervals"""
    print("\n=== Testing Message Expiry Intervals ===")

    broker = os.getenv("MQTT_BROKER", "localhost")
    port = int(os.getenv("MQTT_PORT", "1883"))
    username = os.getenv("MQTT_USERNAME", "yoda")
    password = os.getenv("MQTT_PASSWORD", "")

    if not password:
        print("❌ ERROR: MQTT_PASSWORD environment variable not set")
        return False

    client = mqtt.Client(
        client_id="test-expiry-client",
        protocol=mqtt.MQTTv5,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2
    )

    client.username_pw_set(username, password)

    messages_received = []

    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            messages_received.append(payload)
            print(f"📨 Received: {payload}")
        except:
            print(f"📨 Received (raw): {message.payload.decode()}")

    client.on_message = on_message

    try:
        client.connect(broker, port, 10)
        client.loop_start()

        # Subscribe to test topics
        test_topic = "/test/expiry"
        client.subscribe(test_topic, qos=1)

        # Publish a message with 30-second expiry
        payload = {
            "test": "expiry_test",
            "timestamp": int(time.time()),
            "message": "This should expire in 30 seconds"
        }

        properties = mqtt.Properties(mqtt.PacketTypes.PUBLISH)
        properties.MessageExpiryInterval = 30  # 30 seconds

        print("📤 Publishing test message with 30s expiry...")
        result = client.publish(
            topic=test_topic,
            payload=json.dumps(payload),
            qos=1,
            retain=True,
            properties=properties
        )
        result.wait_for_publish()

        # Wait a bit and check if message is received
        time.sleep(2)
        if messages_received:
            print("✅ Message published and received successfully")
        else:
            print("⚠️  Message published but not received (may be timing issue)")

        # Wait for expiry and check if message disappears
        print("⏳ Waiting 35 seconds for message expiry...")
        time.sleep(35)

        # Try to receive again - should get nothing if expiry worked
        messages_received.clear()
        client.subscribe(test_topic, qos=1)
        time.sleep(2)

        if not messages_received:
            print("✅ Message expired and was cleaned up successfully")
            success = True
        else:
            print("❌ Message still exists after expiry time")
            success = False

        client.loop_stop()
        client.disconnect()
        return success

    except Exception as e:
        print(f"❌ Expiry test error: {e}")
        return False

def main():
    """Run all Phase 1 tests"""
    print("🚀 Chainloot MQTT Phase 1 Testing Script")
    print("=" * 50)

    # Check environment
    required_vars = ["MQTT_PASSWORD"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"❌ Missing required environment variables: {', '.join(missing)}")
        print("\nSet these before running:")
        print("export MQTT_BROKER=your_broker_host")
        print("export MQTT_PORT=1883")
        print("export MQTT_USERNAME=yoda")
        print("export MQTT_PASSWORD=your_password")
        sys.exit(1)

    # Run tests
    connectivity_ok = test_mqtt_connectivity()
    expiry_ok = test_message_expiry() if connectivity_ok else False

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"   Connectivity: {'✅ PASS' if connectivity_ok else '❌ FAIL'}")
    print(f"   Message Expiry: {'✅ PASS' if expiry_ok else '❌ FAIL'}")

    if connectivity_ok and expiry_ok:
        print("\n🎉 PHASE 1 TESTS PASSED - Ready for Phase 2 implementation!")
        sys.exit(0)
    else:
        print("\n💥 PHASE 1 TESTS FAILED - Fix issues before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">c:\Users\jbras\GitHub\chainloot\test_mqtt_phase1.py