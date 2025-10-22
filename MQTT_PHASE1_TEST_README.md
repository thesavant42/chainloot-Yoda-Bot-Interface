# MQTT Phase 1 Testing Script

This script tests the MQTT 5.0 implementation for the Chainloot Yoda Bot Interface.

## Prerequisites

1. **MQTT Broker Running**: Mosquitto must be running with MQTT 5.0 support
2. **Authentication**: Broker must require username/password authentication
3. **Python Dependencies**: `paho-mqtt>=1.6.0` must be installed

## Setup Environment Variables

Before running the script, set these environment variables:

```bash
export MQTT_BROKER=your_broker_host  # e.g., localhost, 192.168.1.98, or mosquitto
export MQTT_PORT=1883                 # MQTT broker port
export MQTT_USERNAME=yoda             # MQTT username
export MQTT_PASSWORD=your_password    # MQTT password (required)
```

## Running the Tests

```bash
python test_mqtt_phase1.py
```

## What It Tests

1. **MQTT Connectivity**: Verifies connection to broker with authentication
2. **Message Expiry**: Tests MQTT 5.0 Message Expiry Interval functionality

## Expected Output

### Success:
```
🚀 Chainloot MQTT Phase 1 Testing Script
==================================================
=== Testing MQTT Connectivity ===
Connecting to localhost:1883 as yoda
✅ Connected successfully

=== Testing Message Expiry Intervals ===
📤 Publishing test message with 30s expiry...
📨 Received: {'test': 'expiry_test', 'timestamp': 1234567890, 'message': 'This should expire in 30 seconds'}
✅ Message published and received successfully
⏳ Waiting 35 seconds for message expiry...
✅ Message expired and was cleaned up successfully

==================================================
📊 TEST RESULTS:
   Connectivity: ✅ PASS
   Message Expiry: ✅ PASS

🎉 PHASE 1 TESTS PASSED - Ready for Phase 2 implementation!
```

### Failure (Missing Password):
```
❌ ERROR: MQTT_PASSWORD environment variable not set

Set these before running:
export MQTT_BROKER=your_broker_host
export MQTT_PORT=1883
export MQTT_USERNAME=yoda
export MQTT_PASSWORD=your_password
```

## Troubleshooting

- **Connection Failed**: Check broker is running and credentials are correct
- **Expiry Test Failed**: Verify broker supports MQTT 5.0 and expiry intervals
- **Import Error**: Install `paho-mqtt>=1.6.0` with `pip install paho-mqtt>=1.6.0`

## Next Steps

If tests pass, Phase 1 is complete and you can proceed to Phase 2 (heartbeat publishing and will messages).</content>
<parameter name="filePath">c:\Users\jbras\GitHub\chainloot\MQTT_PHASE1_TEST_README.md