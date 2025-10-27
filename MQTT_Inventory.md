# MQTT Around The App

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

### CORE

These modules are essential to the operation of the app. They are not candidates for removal. They should be evaluated for logic errors.

### app.py

`docker\chainloot\chainlit\app.py`

- Core Application!

**Line 547-554**

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
- Seems duplicative, perhaps a candidate for archive or refactor

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
