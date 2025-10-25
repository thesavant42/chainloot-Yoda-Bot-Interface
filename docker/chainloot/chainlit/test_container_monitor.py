#!/usr/bin/env python3
"""
Test script for container monitor
"""

import asyncio
import sys
import os
sys.path.append('.')

from lib.container_monitor import get_container_monitor

# Mock container data based on the JSON structure you provided
MOCK_CONTAINER_DATA = [
    {
        "Id": "sha256:abc123...",
        "Names": ["/chainloot-postgres-1"],
        "Image": "postgres:16",
        "State": "running",
        "Status": "Up 2 hours (healthy)",
        "Ports": [{"IP": "0.0.0.0", "PrivatePort": 5432, "PublicPort": 5432, "Type": "tcp"}],
        "SizeRootFs": 1073741824
    },
    {
        "Id": "sha256:def456...",
        "Names": ["/chainloot-chainlit-1"],
        "Image": "chainlit:latest",
        "State": "running",
        "Status": "Up 2 hours",
        "Ports": [{"IP": "0.0.0.0", "PrivatePort": 8100, "PublicPort": 8100, "Type": "tcp"}],
        "SizeRootFs": 2147483648
    },
    {
        "Id": "sha256:ghi789...",
        "Names": ["/chainloot-tts-webui-1"],
        "Image": "tts-webui:latest",
        "State": "running",
        "Status": "Up 2 hours (healthy)",
        "Ports": [{"IP": "0.0.0.0", "PrivatePort": 7778, "PublicPort": 7778, "Type": "tcp"}],
        "SizeRootFs": 5368709120
    }
]

async def test_container_monitor():
    """Test the container monitor functionality"""
    print("Testing Container Monitor...")

    monitor = get_container_monitor()

    # Test 1: Test data organization with mock data
    print("\n1. Testing data organization...")
    organized = monitor.organize_container_data(MOCK_CONTAINER_DATA)
    containers = organized.get("containers", {})
    services = organized.get("services", {})

    print(f"✓ Organized mock data into {len(containers)} containers and {len(services)} services")
    print(f"  Containers: {list(containers.keys())}")
    print(f"  Services: {list(services.keys())}")

    # Verify container data structure
    for name, data in containers.items():
        required_keys = ["timestamp", "cpu_percent", "memory_usage", "memory_limit", "memory_percent", "status"]
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            print(f"✗ Container {name} missing keys: {missing_keys}")
        else:
            print(f"✓ Container {name} has correct data structure")

    # Verify service data structure
    for name, data in services.items():
        required_keys = ["available", "status", "healthy", "image", "ports"]
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            print(f"✗ Service {name} missing keys: {missing_keys}")
        else:
            print(f"✓ Service {name} has correct data structure")

    # Test 2: Check MQTT publisher exists and has correct methods
    print("\n2. Testing MQTT publisher...")
    if hasattr(monitor, 'mqtt_publisher') and monitor.mqtt_publisher:
        print("✓ MQTT publisher initialized")
        # Check if methods exist
        methods = ['publish_resource_usage', 'publish_service_status', 'publish_emotion']
        for method in methods:
            if hasattr(monitor.mqtt_publisher, method):
                print(f"  ✓ {method} method available")
            else:
                print(f"  ✗ {method} method missing")
                return False
    else:
        print("✗ MQTT publisher not initialized")
        return False

    # Test 3: Test MQTT publishing (without actually connecting)
    print("\n3. Testing MQTT publishing structure...")
    try:
        # This will fail to connect but should not crash
        monitor.publish_container_data(organized)
        print("⚠ MQTT publish attempted (expected to fail without broker)")
    except Exception as e:
        print(f"✗ MQTT publish failed with error: {e}")
        return False

    # Test 4: Test emotion classification
    print("\n4. Testing emotion classification...")
    from lib.container_monitor import classify_text_emotion, publish_emotion_data

    test_text = "Hello world"
    emotion_result = classify_text_emotion(test_text)
    if "error" not in emotion_result and "dominant_emotion" in emotion_result:
        print(f"✓ Emotion classification working: {emotion_result['dominant_emotion']}")
    else:
        print(f"✗ Emotion classification failed: {emotion_result}")
        return False

    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(test_container_monitor())
    sys.exit(0 if result else 1)