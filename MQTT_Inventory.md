# MQTT Around The App

A Catalog of MQTT in the Chainloot environment

## NOTE! The passwords must be changed when installed in production

- demo url: mqtt://192.168.1.98:1883
    (note: This is a LAN service, so it MUST be referenced by LAN IP, not Docker hostname).
- demo clientId: vscode
- demo user: yoda
- demo password: yoda

---

## Summary of MQTT in Chainloot

### Background Information

  MQTT began in the chainloot app as a way to create and manage a state machine for the bots' emtional status while chatting with a User. The idea was (and is still) to use the emotional classifier to update an MQTT topic with the bot's dominant emotion, allowing for programatic responses as a result (Motor macros, animation loops, voice inflection, etc.)

### Problem Statements

  But MQTT, being useful for more than feelings, quickly proved to be a worthwhile option to manage service monitoring and container monitoring.

  Code drift has begun to take hold as more entities are developing the software, as a result theres a confusingly named mis-matched pile of code that needs to be rectified and centralized.

  The core functionality of GPU/CPU/MEM/TEMP does not seem to be properly updating.

- The stats don't update every 60 seconds like they should
- Seem to only run at start
- As a result, all reported statistics are inaccurate

### Root Cause Identified

#### CRITICAL FINDINGS - Three Monitoring Systems with Different Purposes

There are **THREE separate monitoring systems** in the codebase, each with legitimate architectural purposes:

1. **system_monitor_script.py** (via cron at host level)
   - Monitors GPU/CPU/Memory stats at the Docker HOST level, not inside container
   - Justification: GPU is a shared resource used by multiple applications; must be monitored externally
   - Runs via cron job configured in `start.sh`
   - Publishes to: `/chainloot/system/*` namespace

2. **container_monitor.py** (async coroutine in app.py)
   - Monitors individual container health/status (name, state, uptime)
   - Justification: Container-level operational concerns are separate from system-level resource concerns
   - Runs in app.py event loop at 30s intervals
   - Publishes to: `/chainloot/system/containers/*` namespace

3. **Emotional classifier system** (via mqtt_publisher.py)
   - Publishes bot emotional state based on sentiment analysis
   - Separate concern from infrastructure monitoring
   - Publishes to: `/chainloot/<profile>/*` namespace

**THE STALE DATA PROBLEM**: `system_monitor.log` shows identical statistics repeated across multiple runs:

```txt
Published system stats: CPU 0.2%, Memory 23.0%, GPU count: 1
Published system stats: CPU 0.2%, Memory 23.0%, GPU count: 1
Published system stats: CPU 0.2%, Memory 23.0%, GPU count: 1
```

**Cron IS running** (confirmed by presence of log entries), but the published data is frozen. This indicates the issue is NOT with cron execution, but rather with:

- **HOW the data is being collected** (GPUtil/psutil may be returning stale values)
- **HOW the data is being published to MQTT** (publish mechanism may have a bug)
- **Timing of GPU stat collection** (GPU driver may not be returning fresh data to the container)

### Objective

- Identify the cause of the MQTT Stats reporting failure
- Reduce code complexity and eliminate drift by refactoring/consolidating MQTT in Chainloot.

This document aims to catalog MQTT in the application, classify it, cluster it with similar services, and document the true process for MQTT in the Chainloot environment.

---

## Files with MQTT

These are the paths that have MQTT code in them. These should all be reviewed to determine the answers to these questions for each instance:

- Is this code meant to be in production, or only in development and testing?
- Is this feature a duplicate mqtt feature?
- Can this code be removed?
- Does this code do WHAT we want, WHEN we want it to?

---

## Analysis: Why GPU Stats Are Stale

### System Monitor Lifecycle

Looking at the code flow in `start.sh`:

1. **Line 35-36**: Badge subscriber starts (works fine, subscribes to MQTT topics)
2. **Line 39-41**: Cron job is CONFIGURED via `/etc/cron.d/container_monitor` to run every 60 seconds
3. **Line 46-47**: Cron is activated with `crontab` command
4. **Line 50-52**: `system_monitor_script.py` runs ONCE manually for initial stats

**THE PROVEN FACTS**:

- Cron IS executing (confirmed by log entries in `system_monitor.log`)
- Data remains frozen across multiple cron executions
- Badge subscriber is correctly subscribing and receiving MQTT data

**THE ACTUAL PROBLEM**: Despite cron running the script repeatedly, the GPU/CPU stats published to MQTT never change. The bug exists in the data collection, MQTT publishing, or GPU driver access pipeline—NOT in the cron scheduling.

### CORE

These modules are essential to the operation of the app. They are not candidates for removal. They should be evaluated for logic errors.

### app.py

`docker\chainloot\chainlit\app.py`

- Core Application!

#### app.py Container Monitor Integration (Lines 547-554)

```python
# Start container monitoring for real-time MQTT publishing
container_monitor = get_container_monitor()
container_monitor.start_monitoring(interval=30)  # Publish every 30 seconds
logger.info("Container monitoring started for real-time MQTT publishing")

# Badge subscriber now runs independently in start.sh
logger.info("Badge subscriber runs independently for event-driven badge generation")
```

Line 681-683: Publishes "online" status for the bot's emotional classifier

```python
    # Publish online status to MQTT
    mqtt_publisher = get_mqtt_publisher()
    mqtt_publisher.publish_status(chat_profile_name.lower(), "online", expiry_interval=60)
```

Line 689-703: Publishes "feelings" status for the bot's emotional classifier

```python
    # Publish idle status and neutral emotion to MQTT
    chat_profile_name = cl.user_session.get("chat_profile")
    if chat_profile_name:
        mqtt_publisher = get_mqtt_publisher()
        mqtt_publisher.publish_status(chat_profile_name.lower(), "idle", expiry_interval=300)
        
        # Publish neutral emotion when going idle
        neutral_emotion = {
            "dominant_emotion": "neutral",
            "dominant_score": 1.0,
            "weights": {"neutral": 1.0}
        }
        mqtt_publisher.publish_emotion(chat_profile_name.lower(), neutral_emotion, expiry_interval=300)
        logger.info(f"Published idle status and neutral emotion for {chat_profile_name}")
    
        # Stop container monitoring
        container_monitor = get_container_monitor()
        container_monitor.stop_monitoring()
        logger.info("Container monitoring stopped")        
```

Line 775-789

```python
async def cleanup_on_exit():
    """Clean up MCP resources and MQTT on app shutdown"""
    try:
        active_manager = get_active_mcp_manager()
        await active_manager.cleanup()
        logger.info("MCP resources cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up MCP resources: {e}")
    
    try:
        mqtt_pub = get_mqtt_publisher()
        mqtt_pub.disconnect()
        logger.info("MQTT disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting MQTT: {e}")

```

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\start.sh`

- Line 3-19 Cleanup function to kill mqtt process

```bash

# Function to cleanup background processes
cleanup() {
    echo "Shutting down services..."
    if [ ! -z "$CHAINLIT_PID" ]; then
        echo "Stopping Chainlit server (PID: $CHAINLIT_PID)..."
        kill $CHAINLIT_PID 2>/dev/null
    fi
    if [ ! -z "$MQTT_PID" ]; then
        echo "Stopping MQTT MCP server (PID: $MQTT_PID)..."
        kill $MQTT_PID 2>/dev/null
    fi
    # Remove cron job
    echo "Removing container monitoring cron job..."
    rm -f /etc/cron.d/container_monitor
    service cron reload 2>/dev/null || true
    exit 0
}
```

- Line 28-50: Start monitoring processes

```bash
# Start MQTT MCP server in background
echo "Starting MQTT MCP server on port 8100..."
mqtt-mcp &
MQTT_PID=$!
echo "MQTT MCP server started with PID: $MQTT_PID"

# Start badge subscriber in background -
echo "Starting badge subscriber..."
python3 /app/lib/badge_subscriber.py &
BADGE_PID=$!
echo "Badge subscriber started with PID: $BADGE_PID"

# Add cron job to run container monitor every 2 minutes
echo "Setting up container monitoring cron job..."
echo "* * * * * /usr/local/bin/python3 /app/lib/system_monitor_script.py >> /app/system_monitor.log 2>&1" >> /etc/cron.d/container_monitor
chmod 0644 /etc/cron.d/container_monitor
crontab /etc/cron.d/container_monitor


# Run initial system monitoring
echo "Running initial system monitoring..."
chmod +x /app/lib/system_monitor_script.py
/usr/local/bin/python3 /app/lib/system_monitor_script.py
```

### mcp_servers.json

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\config\mcp_servers.json`

```json
    "mqtt": {
      "command": "mcp-proxy",
      "args": ["--transport", "streamablehttp", "http://127.0.0.1:8100/mcp/"],
      "env": {},
      "description": "MQTT broker communication via embedded server"
    },
```

### badge_subscriber.py

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\lib\badge_subscriber.py`

- Badge Subscriber Script
- Subscribes to MQTT system stats and generates SVG badges.

### container_monitor.py

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\lib\container_monitor.py`

- "Lightweight Container Monitor for Chainlit"
- Fetches Docker container data via HTTP API and publishes to MQTT.

### mcp_tool_processor.py

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\lib\mcp_tool_processor.py`

- Handles which mcp tools bot can use, including mqtt-mcp

### message_processor.py

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\lib\message_processor.py`

### mqtt_publisher.py

- Handles incoming messages, including emotional classification and mqtt publishing

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\lib\mqtt_publisher.py`

- MQTT Publisher, just like it says.
- **This is an important file**

### mqtt_server.py

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\lib\mqtt_server.py`

- Instrumentation for the mqtt-mcp service.

### system_monitor_script.py *

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docker\chainloot\chainlit\lib\system_monitor_script.py`

- "Collects system and GPU stats and publishes to MQTT"
- **CRITICAL**: This script is the SOURCE of GPU/CPU stats for badges
- **BUG**: Relies on cron job in `start.sh` which may not be executing properly
- Runs via: `* * * * * /usr/local/bin/python3 /app/lib/system_monitor_script.py` (every minute)
- **DIAGNOSIS NEEDED**: Verify cron daemon is running inside container

### mosquitto.conf

`mosquitto.conf`

- config file for the mqtt daemon

### last_system_stats.json

`docker\chainloot\chainlit\last_system_stats.json` *

- JSON otuput from  system and GPU keys, docker api
- Q: Why is it writing to the chainlit container docker root? The JSON we're writing to disk as part of the monitoring lifecycle should be in one of the chainlit app's `public` subfolders, as these are accessible across the LAN and hosted by chainlit.

## Utilities

`./yoda.mqtt`

- Connection file for a vSCode MQTT Extension. Useful for monitoring mqtt from the IDE.
- Helpful, no need to remove.

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docs\mqtt_dump.py`

- Utility to dump mqtt data from mosquitto


## Logging *

### system_monitor.log *

`docker\chainloot\chainlit\system_monitor.log` *

- Out from system_monitor_script, but it looks like it's reporting the same exact data, which seems improbable over multiple runs and **probably indicates a bug.**

```txt
...
Starting system monitoring...
Wrote system stats JSON to /app/last_system_stats.json
Published system stats: CPU 0.4%, Memory 23.0%, GPU count: 1
System monitoring complete.
Starting system monitoring...
Wrote system stats JSON to /app/last_system_stats.json
Published system stats: CPU 0.2%, Memory 23.0%, GPU count: 1
System monitoring complete.
Starting system monitoring...
Wrote system stats JSON to /app/last_system_stats.json
Published system stats: CPU 0.2%, Memory 23.0%, GPU count: 1
System monitoring complete.
...
```

### badge_subscriber.log *

`docker\chainloot\chainlit\badge_subscriber.log` *

- Log for Badge Subscriber, a script that subscribes to MQTT topics of interest for monitoring and generates "anybadge" badges in SVG for those topics.
- Seems to be correctly polling every minute or so, but the data in MQTT seems to be inaccurate.

## Investigation Plan: Debugging Stale GPU Stats

### Root Cause Theory - PROVEN

**DEFINITIVE PROOF**: `last_system_stats.json` contains fresh, current data on every cron execution:
- Timestamp changes every 60 seconds
- GPU memory_util_percent and temperature values are current
- File is being atomically written with new data

**CONCLUSION**: Data collection from Docker API is working perfectly. The bug is in `system_monitor_script.py`'s MQTT publishing mechanism. Fresh data is collected and written to JSON, but NOT published to MQTT topics that `badge_subscriber` subscribes to.

**The bug is in these lines of `system_monitor_script.py`:**
- Lines 115-125: The `publish.single()` call for the full `/chainloot/system/stats` topic
- Lines 128-155: The per-key publish loop for individual topics
- Lines 158-180: The GPU-specific publish loop

One of these publish mechanisms is broken or not executing.### Diagnostic Commands (Run in Container)

#### Step 1: Confirm JSON file has fresh data

```bash
cat /app/last_system_stats.json | python3 -m json.tool
```

Run this multiple times with delays. The `timestamp`, GPU `memory_util_percent`, and `temperature` should change on each run. If they do, data collection is working. (This confirms the bug is in MQTT publishing, not data collection.)

#### Step 2: Check if MQTT topics are receiving updates

Connect to MQTT broker and subscribe to system stats topics:

```bash
mosquitto_sub -h 192.168.1.98 -u yoda -P yoda -t "/chainloot/system/+/+" | head -20
```

Run `system_monitor_script.py` manually while watching this output. Do new values appear in MQTT immediately after script execution? If not, the publish mechanism is broken.

#### Step 3: Test GPU data freshness from Docker API

Query the Docker REST API directly to see if it returns fresh GPU data:

```bash
curl -s http://host.docker.internal:2375/v1.43/containers/json | python3 -m json.tool | grep -i gpu
```

Run this multiple times with a few seconds between runs. Do GPU values change? If all readings are identical, the Docker daemon's API is returning cached data.

Alternatively, inspect container stats endpoint which may have real-time metrics:

```bash
curl -s http://host.docker.internal:2375/v1.43/containers/<container_id>/stats | python3 -m json.tool
```

#### Step 4: Inspect `system_monitor_script.py` publish calls

Look at the actual MQTT publish logic in `system_monitor_script.py` (around lines 120-180). Check:

- Are `retain=True` flags preventing new messages from being visible?
- Are publish calls actually executing, or is an exception being silently caught?
- Is the payload being formatted correctly?

### Likely Culprits

**Most likely**: The Docker daemon's REST API endpoint is returning cached GPU stats instead of fresh values. GPUtil queries this API, so stale Docker API data → stale GPU data → stale MQTT messages. This is a host-level Docker daemon issue, not a script issue.

**Secondary possibility**: The `publish.single()` calls in `system_monitor_script.py` with `retain=True` flags. MQTT retained messages may not update if the publish payload is identical to the previous retained value. Combined with stale Docker API data, this would perpetuate the stale values indefinitely.

**To rule out**: The cron execution itself—logs prove this is working correctly.

## Removal Candidates *

These files might be safe to remove, but further investigation is still required. Do not modeify these, for now.

### container_monitor.py.bak

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docs\container_monitor.py.bak`

- Backup file for container_monitor.py
- Candidate for deep archive

### OLD_container_monitor_script.py

`C:\Users\jbras\GitHub\chainloot-Yoda-Bot-Interface\docs\OLD_container_monitor_script.py`

- Deprecated monitoring script, renamed to determine blast radius of deleting the file.

## Links

### Current Badge Status Page

-[https://192.168.1.98:8443/public/index.html](https://192.168.1.98:8443/public/index.html)
    - HTML embedding the 4 status badges for quick testing/verification
    - Part of Chainlit container.

### Anybadge - Used to create the badges for status

- [https://github.com/jongracecox/anybadge](https://github.com/jongracecox/anybadge)
- Latest version: 1.16.0
- Installed: 1.16.0
- Use GitHub MCP tools to query.

- [https://deepwiki.com/jongracecox/anybadge](https://deepwiki.com/jongracecox/anybadge)
- Deepwiki offers constructive insights into git repositories
- Use Deepwiki mcp tools to query
