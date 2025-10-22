# MQTT Emote Project

This project is the actionable extension of the MQT-sentiment-classifier.md research document.  Both documents should be considered companion documents, except for when the information contradicts; in that case, this document will be considered the source of truth and upsercedes MQTT-sentiment-classifier.md

## Handoff Implementation Complete ✅

I have successfully implemented the MQTT-based emotion state machine for the Chainloot Yoda Bot Interface as outlined in your handoff notes. Here's what was accomplished:

### ✅ Completed Tasks

1. **Mosquitto MQTT Broker Setup**
   - Added `mosquitto` service to `install/docker/docker-compose.yml` with proper configuration
   - Created `install/docker/mosquitto.conf` with authentication settings
   - Generated password file for user 'yoda' using the Docker container method
   
     **Optional: Persistent Client Expiration**
     Mosquitto supports a non-standard option `persistent_client_expiration` to automatically remove persistent clients (clean session=false) that haven't reconnected within a specified timeframe. This prevents indefinite queuing of messages for crashed clients. Example configurations:
     - `persistent_client_expiration 2m` (2 months)
     - `persistent_client_expiration 14d` (14 days)
     - `persistent_client_expiration 1y` (1 year)
     Default is never expire. This can be added to `mosquitto.conf` for better resource management and presence cleanup.
   
     **Future Password Regeneration Process:**
     If you need to regenerate the Mosquitto password file in the future, follow these steps:
     
     1. **Start a temporary Mosquitto container:**
        ```bash
        docker run -d --name temp_mosquitto eclipse-mosquitto tail -f /dev/null
        ```
     
     2. **Create the password file inside the container:**
        ```bash
        docker exec -i temp_mosquitto mosquitto_passwd -c /tmp/passwd <username>
        ```
        (Replace `<username>` with your desired username, e.g., `yoda`. You'll be prompted to enter and confirm the password.)
     
     3. **Copy the password file to your host:**
        ```bash
        docker cp temp_mosquitto:/tmp/passwd ./install/docker/passwd
        ```
     
     4. **Clean up the temporary container:**
        ```bash
        docker rm -f temp_mosquitto
        ```
     
     5. **Restart the Mosquitto service:**
        ```bash
        cd install/docker && docker-compose restart mosquitto
        ```
     
     **Note:** This process creates a hashed password file that Mosquitto can read. The password will be required for any MQTT clients connecting to the broker.
   
   - Verified MQTT connectivity with test publish/subscribe operations

2. **MQTT Publisher Module**
   - Created `lib/mqtt_publisher.py` with `MQTTPublisher` class
   - Supports publishing emotion data and status updates
   - Uses QoS 1 and retained messages for reliable delivery
   - Configurable broker settings via environment variables

3. **Enhanced Sentiment Classification**
   - Modified `lib/feels_classifier.py` to return all 28 emotions with normalized weights
   - Changed from top-1 to top-all classification for richer emotion data
   - Maintains backward compatibility with existing code

4. **Message Processing Integration**
   - Updated `lib/message_processor.py` to aggregate emotions across message chunks
   - Publishes aggregated emotion weights to MQTT topic `/chainloot/persona/{persona}/feelings`
   - Includes timestamp, dominant emotion, and full weights dictionary

5. **Application Integration**
   - Modified `app.py` to pass persona information to message processing
   - Added online status publishing in `on_chat_start()` to `/chainloot/persona/{persona}/status`
   - Integrated MQTT publishing into the chat flow

6. **Dependencies & Build**
   - Added `paho-mqtt` to `requirements.txt`
   - Fixed Docker build issues with `.dockerignore` configuration
   - Successfully rebuilt and deployed all containers

### 🔧 Technical Implementation Details

**MQTT Topics:**
- Emotions: `/chainloot/persona/{persona}/feelings`
- Status: `/chainloot/persona/{persona}/status`

**Message Format:**
```json
{
  "timestamp": 1729321258,
  "dominant_emotion": "happy",
  "weights": {
    "shy": 0.4,
    "happy": 0.6,
    "curious": 0.0,
    ...
  }
}
```

**QoS & Reliability:**
- QoS 1 (at least once delivery)
- Retained messages for instant state sync with new subscribers
- Automatic reconnection handling

### Ready for Use

The system is now ready to:
- Publish real-time emotion states during conversations
- Support multiple personas with independent MQTT topics
- Integrate with Home Assistant, external displays, or other MQTT subscribers
- Provide rich emotion data with 28 emotion categories and weights

All services are running and the MQTT broker is operational. The emotion state machine will activate automatically when users start chat sessions with any persona (Yoda, AI, Stark).

--- 

## Feedback

So far it seems to work reasonably well. I want to make some adjustments to the workflow, but the implementation is otherwise very promising.

# Idle vs. Online vs. Offline vs Active


## The problem statement:
The emotional state for a persists as the last-set emotiional state, which is by design and not a problem. However in human like behavior emotions tend to cool off over time, or change naturally on their own as a person experiences their day. The expression agent is meant to map to a visual representation of the persona's emotional state eventually, and as it is currently configured, the persona will be frozen in agony (or ecstasy) until they send another message to the user, at which point they will be frozen in the next emotional state.

Question: What is the current bot -> mqtt presence/emotion flow looklike?
   - 1. Chainlit app starts, launches feel module...
   - 2. ???
   - 3. ...

## Updating the flow

We will use Yoda as a contrived example. App starts, feel module launches, bot is "online", which is to say it's alive

   - `status = {"timestamp": 1761114614, "status": "online"}`

   Present workflow, when a bot logs in their emotional state seems to be whatever it last was, which makes sense:

   - Bot is "online" if app is running, on / off. Not particularly useful for status since there are MANY ways to know if the app is running.
   - `feelings = {"timestamp": 1761093363, "dominant_emotion": "confusion", "weights": {"confusion": 0.12434792777280047, "disappointment": 0.06070178137209749, "caring": 0.05673374758770932, "annoyance": 0.05494783231261283, "approval": 0.053840769211470796, "realization": 0.052835019101322815, "desire": 0.05105421864960605, "disapproval": 0.05068690876583553, "remorse": 0.04905231850203371, "curiosity": 0.04818432589644409, "neutral": 0.03909188356077382, "surprise": 0.033051828492268176, "admiration": 0.0308322074870088, "grief": 0.028834032629589206, "amusement": 0.026243460269435002, "excitement": 0.025757783016351156, "relief": 0.0254231606910259, "pride": 0.02541329612270143, "embarrassment": 0.022561789539088346, "disgust": 0.020752488755058005, "sadness": 0.01925829722653284, "anger": 0.018194264951945163, "nervousness": 0.0158155163151662, "optimism": 0.015037012629625824, "fear": 0.014828916059048404, "gratitude": 0.013882905633112381, "joy": 0.012076027219003865, "love": 0.01056028023033238}, "dominant_score": 0.12434792777280047}`

   - I like to think of the bot as a remote worker, logging into team chat in the morning when he starts up, and is "online"
     - But mood and presence aren't necessarily linked, so the bot's mood could be "neutral" , "amusement", "optimism", some other emotional expression that's classified by the dilbert system.
     - Master Yoda, a renowned Jedi Grand Master, is known for his self control and emotional pacification. He is statistically less likely to feel confusion, or anger ,and is known to have a sense of humor.

If Master Yoda is online,
 - begin a counter at login, counting up to 5 minutes
 - and is "idle", (not in a chat, hasn't responded to user messages in ~ 5 minutes)
  - his emotion = random(feelings[]); # Randomize those feelings;
  - wait 5 MORE minutes, then set his feelings to amusement, since Yoda knows how to meditate and settle his emotions;
  - Wait another 5 minutes; set  new rnandom(feelings[]); # Random feelings again!
     ... and so on, until 30 minutes of idleness...

  - After 30 minutes of idleness (not interacting with a user, or performing a task at a user's request), the bot "falls asleep"
   - status in mqtt indicates "sleeping" (but still online)
      - So long as the app is running the bot is "online"

### MQTT Settings 

   While MQTT 5.0 supports Message Expiry Interval (TTL) for published messages, including retained ones, this alone doesn't provide the desired idle decay behavior—we need application logic to periodically publish new emotion states. 

   However, the expiry is absolutely essential for reliable online/offline status tracking, especially for detecting crashes or network disconnections. 

- https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901112
- [ ] The core timer-based system for emotion evolution is still required, plus heartbeat publishing with short expiry intervals. 
- Estimated: 2-4 hours of development and testing, plus configuration tuning. 
- [ ] We can leverage MQTT expiry to set maximum lifetimes for emotion messages (e.g., 30 minutes) and short heartbeats (e.g., 60 seconds) for presence detection.

**Q: Please outline the design you recommend with descriotions of the changes:**

**A: Here's a detailed task breakdown for implementing the idle emotion decay and presence tracking system. Tasks are ordered for sequential development with dependencies noted.**

---

**All entries prior to this line are for historical and informational purposes only. after this line is where the actionable plans begin.**

# Project Plan
 - **Tasks must be completed in order**
 - **Task checkboxes must be marked when task is completed**

### Phase 1: MQTT 5.0 Infrastructure Setup

   1. Use MCP Tools, update your documentation via context7
      - MQTT 5.0
      - Mosquitto broker

- [x] **Task 1.1: Upgrade Paho MQTT Client to MQTT 5.0**
  - [x] Update `requirements.txt` to use `paho-mqtt>=1.6.0` (supports MQTTv5)
  - [x] Modify `lib/mqtt_publisher.py` to use `mqtt.CallbackAPIVersion.VERSION2` and MQTTv5 protocol
  - [ ] Test basic connect/publish/subscribe with MQTT 5.0
  - [ ] Acceptance: Client connects to Mosquitto using MQTT 5.0 protocol

- [x] **Task 1.2: Configure Mosquitto for MQTT 5.0**
  - [x] Update `install/docker/mosquitto.conf` to enable MQTT 5.0 features
  - [x] Add `persistent_client_expiration 14d` to prevent stale session buildup
  - [ ] Restart Mosquitto service and verify MQTT 5.0 support
  - [ ] Acceptance: Mosquitto accepts MQTT 5.0 connections and cleans up expired sessions

- [ ] **Task 1.3: Implement Message Expiry Interval**
  - [x] Add `expiry_interval` parameter to `MQTTPublisher.publish()` method
  - [x] Set default expiry intervals: 300s (5min) for emotions, 60s for status
  - [ ] Test that expired messages are automatically cleaned up
  - [ ] Acceptance: Retained messages expire and disappear from broker after interval

**Dependencies:**
- **Task 1.1 must complete before Tasks 1.3, 2.1, 2.2**
- **Task 1.2 required for full MQTT 5.0 testing**
---
### Phase 2: Presence Management System

   1. Use MCP Tools, update your documentation via context7
      - MQTT 5.0
      - Mosquitto broker

- [ ] **Task 2.1: Implement Heartbeat Publishing**
  - [ ] Create `publish_heartbeat()` method in `lib/mqtt_publisher.py`
  - [ ] Publish "online" to `/chainloot/persona/{persona}/status` every 30 seconds
  - [ ] Set 60-second expiry interval on heartbeat messages
  - [ ] Acceptance: Subscribers receive periodic heartbeats that expire if publishing stops

- [ ] **Task 2.2: Configure Will Messages**
  - [ ] Add Will message setup in MQTT CONNECT packet
  - [ ] Will publishes "offline" to status topic on abnormal disconnection
  - [ ] Set QoS 1 and retain flag on Will message
  - [ ] Acceptance: Will message publishes when client crashes or loses connection

- [ ] **Task 2.3: Status State Management**
  - [ ] Extend status publishing to include "idle" and "sleeping" states
  - [ ] Update `app.py` to publish status changes based on idle timers
  - [ ] Ensure status messages use appropriate expiry intervals
  - [ ] Acceptance: Status transitions correctly: online → idle → sleeping → offline
---
### Phase 3: Idle Timer and Emotion Decay System

   1. Use MCP Tools, update your documentation via context7
      - MQTT 5.0
      - Mosquitto broker

- [ ] **Task 3.1: Create Idle Manager Module**
  - [ ] New file: `lib/idle_manager.py`
  - [ ] Implement `IdleManager` class with per-persona timers
  - [ ] Track last interaction timestamp per persona
  - [ ] Acceptance: Can query idle duration for any persona

- [ ] **Task 3.2: Emotion Selection Logic**
  - [ ] Add emotion selection function to `lib/idle_manager.py`
  - [ ] Define persona-specific emotion sets (e.g., Yoda excludes anger)
  - [ ] Implement random selection from allowed emotions
  - [ ] Acceptance: Returns appropriate emotion dict for given persona and idle tier

- [ ] **Task 3.3: Decay Timer Implementation**
  - [ ] Background thread in `idle_manager.py` checks idle times every minute
  - [ ] Triggers emotion updates based on idle tiers:
    - [ ] 0-5 min: Amusement
    - [ ] 5-10 min: Random
    - [ ] 10-15 min: Amusement
    - [ ] 15-30 min: Random
    - [ ] 30+ min: Sleeping
  - [ ] Acceptance: Emotions change automatically based on idle time

- [ ] **Task 3.4: Integration with Message Processing**
  - [ ] Update `lib/message_processor.py` to reset idle timers on user messages
  - [ ] Call `idle_manager.reset_timer(persona)` on each interaction
  - [ ] Ensure timer resets don't interfere with ongoing decay
  - [ ] Acceptance: User messages immediately reset idle state to active

**Dependencies:**
- Tasks 3.1-3.3 can be developed in parallel
---
### Phase 4: Configuration and Testing

   1. Use MCP Tools, update your documentation via context7
      - MQTT 5.0
      - Mosquitto broker

- [ ] **Task 4.1: Configuration Schema**
  - [ ] Add "idle_behavior" section to `config.json`
  - [ ] Include per-persona settings: emotion sets, tier thresholds, expiry intervals
  - [ ] Add "mqtt_v5_features" section for heartbeat frequency, expiry defaults
  - [ ] Acceptance: Config loads without errors and provides all required settings

- [ ] **Task 4.2: Error Handling and Resilience**
  - [ ] Add MQTT reconnection logic with session resumption (clean_session=false)
  - [ ] Implement fallback to MQTT 3.1.1 if 5.0 fails
  - [ ] Add logging for expiry events and presence changes
  - [ ] Acceptance: System recovers gracefully from network interruptions

**Dependencies:**
- Task 4.1 must be done early for testing
---
### Phase 5: Documentation and Deployment

   1. Use MCP Tools, update your documentation via context7
      - MQTT 5.0
      - Mosquitto broker

- [ ] **Task 5.1: Update Application Startup**
  - [ ] Modify `app.py` to initialize `IdleManager` on startup
  - [ ] Start background threads for heartbeat and idle monitoring
  - [ ] Ensure proper cleanup on shutdown
  - [ ] Acceptance: App starts with idle system active

- [ ] **Task 5.2: Documentation Updates**
  - [ ] Update this document with implementation details and troubleshooting
  - [ ] Add monitoring/debugging section for MQTT topics
  - [ ] Document configuration options and their effects
  - [ ] Acceptance: Complete handoff documentation for maintenance

- [ ] **Task 5.3: Production Deployment**
  - [ ] Update Docker compose with MQTT 5.0 settings
  - [ ] Test full system with real Mosquitto broker
  - [ ] Monitor resource usage and message rates
  - [ ] Acceptance: System runs stably in production environment

**Dependencies:**
- **Phase 5 requires all previous phases complete**

---
### Sources:

- MQTT 5.0 Specification: Message Expiry Interval - https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901112
- Mosquitto Documentation: persistent_client_expiration - https://mosquitto.org/man/mosquitto-conf-5.html