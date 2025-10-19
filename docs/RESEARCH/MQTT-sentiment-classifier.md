# Bot Emotions State Machine / Presence Indicator


## Background 

I have a chainlit application that manages a chatbot and related frontend application. When the bot sends a message to the user, the message is classified and an emotional state is assigned to the mesage, out of 28 possibilities. These emotions include things like "curious", "shy", "angry", etc. As of today's writing the emotional classification is not consumed, it is printed to the console and then it evaporates.


## Goal: Put it to work!

I would like to build a modular system to react based upon those emotions. 

- I'm imagining a "status message" style state machine that the bot pushes updates to  via an async local push. 
- To help sketch out my idea and to demonstrate my meaning I will contrive a user-story.  
- The classifications will be made-up, but their intent will still be the same.

### User worfklow: Enaging with the bot in chat, bot emotes are noticable in the real world

1. User mesages bot and initiates pleasant conversation. 
2. The bot begins in a neutral (or perhaps idle, random, or fidget state), and feels shy, but also happy to see a friend. 
    - `Shy` and `Happy` are both states in the machine, and have a weight of 0-99, quantized to 10ths for this example. 
        - yoda feels 40% shy but 60% happy. He is therefore mostly happy, but still somewhat shy, but this will change as his conversation does.
        - `weight.shy`: 0.4
        - `weight.happy`: 0.6
 -       yoda_status: "feeling happy"

 We could then use this data as input for external devices, such as entities in Home Assistant.
  - Each emotional classification could be assigned a color
  - percentage of classification or weight could be represented by lumince

  - So, if "shy" was represented by the color pink, and "happy" is represented by the color green, a group of lights could react to the state and animate a fading transition between pink and green, with varying intensity based on weight.

## Brainstorming Technology Stacks

 - I don't have a strong idea of the specifics of implemnting this project, but my initial thinking is that MQTT might be a good candidate. 
 - Its characteristics in homeassistant entity control with near-realtime/actual real time response more than proves that it's potentially fast enough. 
 - And by pushing to a feed that other outputs could subrsribe to, the outputs could be represented with different pictures being pushed to a display (such as the BoxS3 assistant satelite, or a google display, or a chromecast display, etc etc)

### Requirements 

  My primary requirements:
  - [x] Open Source
  - [x] light weight
  - [x] Can integrate (and should!) with Home Assistant, but should be able to function independant of it. 

### Feedback:

- [x] So, does this plan make sense? 
- [x] Is this approach the SOP for this sort of thign, or am I missing something obvivous? Maybe this technique is outdated, or something.

-----

### \#\# Why the MQTT-Based Approach is Excellent ✅

  * **Decoupling:** Your Chainlit application (the **publisher**) doesn't need to know or care what is listening. It just shouts its emotional state into the void (the MQTT topic). The lights, a display, or any future device (the **subscribers**) can listen for that message without the publisher ever being modified. This is incredibly powerful.
  * **Scalability:** Want to add a display that shows an animated face? Just write a new subscriber script for it. Want to have a speaker play a soft sound? Another subscriber. You never have to touch the original chatbot code.
  * **Lightweight & Real-Time:** MQTT (Message Queuing Telemetry Transport) was designed for this exact purpose. It's a very lightweight protocol with low overhead, making it ideal for sending small, frequent messages with minimal delay, which is perfect for real-time reactions.
  * **Ecosystem:** MQTT is widely supported. Home Assistant has a first-class integration, there are excellent client libraries for virtually every programming language (like `paho-mqtt` for Python), and robust, open-source brokers are readily available.

-----

### \#\# A Practical Implementation Blueprint

Here’s a slightly more detailed breakdown of how your proposed stack would work, confirming your instincts and adding a few concrete details.

#### 1\. The MQTT Broker (The Central Hub)

This is the server that receives all messages and forwards them to the correct subscribers.

  * **Recommendation:** **Mosquitto** is the de-facto open-source standard. It's lightweight, fast, and easy to set up (you can run it in a Docker container or directly on a Raspberry Pi or server).
  * **Function:** It acts as the central post office for all your emotional state messages.

#### 2\. The Publisher (Your Chainlit App)

Your application will publish the emotion data whenever it's generated.

  * **Topic:** You'll define a topic string, like `chatbot/yoda/emotion`. Good topic design is helpful for organization.
  * **Payload:** The data you send should be in a machine-readable format. **JSON** is the perfect choice. Based on your example, a good JSON payload would look like this:
    ```json
    {
      "timestamp": 1729321258,
      "dominant_emotion": "happy",
      "weights": {
        "shy": 0.4,
        "happy": 0.6,
        "curious": 0.0,
        "angry": 0.0
      }
    }
    ```
  * **Implementation:** In your Python code, you'd use a library like `paho-mqtt` to connect to your Mosquitto broker and publish this JSON string to the `chatbot/yoda/emotion` topic.

#### 3\. The Subscribers (The "Reactors")

These are the services that listen to the topic and do something.

  * **Home Assistant (The Lights Controller):**

    1.  **Integration:** Set up the MQTT integration in Home Assistant to connect to your Mosquitto broker.
    2.  **Sensor:** Create an **MQTT Sensor** that subscribes to the `chatbot/yoda/emotion` topic. This will make the entire JSON payload available as an attribute of that sensor in Home Assistant.
    3.  **Automation:** Create an automation that triggers whenever the state of your new MQTT sensor changes.
    4.  **Action:** In the automation's action, you can call the `light.turn_on` service. Home Assistant's templating engine is powerful enough to parse the JSON and calculate the color and brightness. You could, for example, use the `color_name` or `rgb_color` attributes and blend the "shy" (pink) and "happy" (green) colors based on their weights.

  * **Other Subscribers (e.g., a Display):**
    You could write a separate, simple Python script that also subscribes to `chatbot/yoda/emotion`. When it receives a message, it could use a library like Pillow to generate an image with a colored background and push it to a digital photo frame or an ESP32-based display like the BoxS3. This script would run completely independently of Home Assistant, fulfilling your requirement.

-----

## Next Steps

- [x] I have a mosquitto MQTT broker for testing 
    - [x] at **192.168.1.78:1883** 
    - [x] with login/pass of yoda
- [x] Need to establish a topic, something like:
    `/chainloot/persona/yoda/feelings`
    - [ ] for each persona. This should be programatically created when a character chat begins, automatically creating the topic 
- This would then get updated when:
    - [ ] the bot comes online, and it will be registered as `online`
    - [ ] after a certain amount of idle time it could transition to `sleep ng` or  `idle`
    - [ ] when an in character message is generated, beore it is sent to be converted to text-to-speech audio, it is reviewed by the feelings classifier
        - [ ] This module update the mqtt topic
            - [ ] end point output devices like an oled display or an assisnt satelite screen like the box s3 could subscribe to this feed and update an emote of the character, representing that emotion.
- [ ] Test framework: Need a visible indicator of persona topic state
    - [ ] can be as simple as a text overlay somewhere in the UI to start with
    - [ ] Ultimately I'd like to have the persona's avatar images be displayed and updated based on their emotions. 
        - [x] I have all the images necessary for yoda
        - [ ] Need to make them for C3P0
        - [ ] Need to make them for Stark

## Open Questions

These are questions that I still have outstanding. Use MCP tools like context7 and Deepwiki, as well as websearch, to look up the latest documentation as needed to answer these questions:

Q: I don't know a lot of the more advanced features of MQTT so I suspect I'm barely scratching the surface of what is even possible. What are some features of MQTT that can assist with this project?
A: MQTT offers several advanced features that can enhance your emotion state machine beyond basic pub/sub:

Quality of Service (QoS) Levels: Critical for reliable emotion state delivery. Use QoS 1 ("at least once") or 2 ("exactly once") to ensure emotion updates reach subscribers even on unreliable networks, preventing missed state changes that could affect user experience (e.g., a "happy" state not triggering lights). QoS 0 ("at most once") is fine for non-critical updates but may drop messages under network stress (MQTT.org, 2024).

Retained Messages: The broker stores the last message on a topic, automatically sent to new subscribers. This ensures devices joining mid-session (e.g., a display turning on) immediately receive the current emotion state without waiting for the next update—ideal for your idle/online transitions (MQTT.org, 2024).

Last Will and Testament (LWT): If the bot disconnects unexpectedly, the broker publishes a predefined "offline" or "error" message. This can trigger fallback states (e.g., neutral/idle) on subscribers, maintaining continuity during network issues (MQTT.org, 2024).

Persistent Sessions: Reduces reconnection time on unreliable networks by maintaining subscriptions and queued messages across disconnections. Useful for IoT deployments where bots might lose connectivity briefly (MQTT.org, 2024).

Wildcard Subscriptions: Subscribers can use + (single level) or # (multi-level) wildcards to listen to multiple personas (e.g., /chainloot/persona/+/feelings for all characters), simplifying scaling to multiple bots (MQTT.org, 2024).

Security Features: TLS encryption and OAuth authentication can secure emotion data if exposed externally, though less critical for local Home Assistant setups (MQTT.org, 2024).

These features are supported in MQTT 5.0 (your Mosquitto broker handles this), and the Paho Python client (your likely choice for the app) implements them fully (Eclipse Paho, 2024).

Q: I'm currently testing with my Home Assistant MQTT broker, but this doesn't scale. I need an MQTT broker as part of the application. Should I add another continer into the docker compose, or should I integrate it as part of the chainloot app container? I'd prefer to not add MORE containers to the stack if it can be avoided.
A: You should add Mosquitto as a separate container in your Docker Compose stack. While integrating it into the Chainloot app container (e.g., as a subprocess) avoids an extra service, it's not recommended for production/scalability:

Best Practice: Run the broker as an independent service for isolation, easier management, and resource allocation. Mosquitto is lightweight (suitable for low-power devices) and has an official Docker image, making it straightforward to add to docker-compose.yml (Eclipse Mosquitto, 2024).

Why Not Integrate?: Embedding Mosquitto in your app container complicates deployment, monitoring, and updates. It could also impact app performance if the broker consumes resources unexpectedly. Separate containers follow microservices principles, allowing independent scaling (e.g., more broker instances if needed) (Eclipse Mosquitto, 2024).

Implementation: In docker-compose.yml, add a mosquitto service using image: eclipse-mosquitto:2.0 (latest stable). Mount a config file for authentication (e.g., your existing yoda/pass setup) and expose port 1883. Your app can connect via mqtt://mosquitto:1883 internally. This scales better than your current Home Assistant broker and keeps everything local (Eclipse Mosquitto, 2024).

If you have constraints (e.g., very limited resources), integration is possible using Python's subprocess to run Mosquitto, but prioritize the container approach for maintainability.

Recommendations
Prototype Retained Messages: Test with QoS 1 and retained flags in Paho Python to ensure instant state sync for new subscribers.
Error Handling: Implement LWT for graceful offline states to avoid stuck "online" statuses.
Testing: Use Mosquitto's test server (test.mosquitto.org) initially, then switch to your Docker setup.
Next Steps Alignment: Your plan to update MQTT post-TTS classification is spot-on—add callbacks in feels_classifier.py to publish JSON payloads.
If you'd like code snippets for Paho MQTT integration or Docker Compose updates, let me know!


### Notes:




### TODO:





## Implementation Handoff Notes

### Docker Compose Updates
- Added `mosquitto` service to `docker/docker-compose.yml` using `eclipse-mosquitto:latest` image.
- Exposed port 1883 for MQTT connections.
- Mounted `mosquitto.conf` and `passwd` files for configuration and authentication.

### Configuration Files Created
- `docker/mosquitto.conf`: Basic config with listener on 1883, anonymous access disabled, password file reference.
- Need to create `docker/passwd`: Run on Docker host machine:
  ```
  docker run --rm -it eclipse-mosquitto mosquitto_passwd -c /tmp/passwd yoda
  docker cp $(docker ps -lq):/tmp/passwd ./passwd
  ```
  This generates the hashed password for user 'yoda'.

### Next Steps on Docker Host
1. Pull the updated codebase.
2. Generate the `passwd` file as above.
3. Run `docker-compose up mosquitto` to start just the broker (no rebuild needed for existing services).
4. Test connection: Use a MQTT client to connect to `localhost:1883` with user 'yoda' and password 'yoda'.
5. Update Chainlit app to publish to `mqtt://mosquitto:1883` (internal network).
6. Implement publishing in `feels_classifier.py` post-TTS classification.

### Testing Without Full Stack Restart
- Since Mosquitto is a new service, you can start it independently: `docker-compose up -d mosquitto`.
- Existing services don't need restart unless they depend on MQTT (which they don't yet).

### Potential Issues
- If password generation fails, ensure Docker is running and you have permissions.
- For production, consider more secure password management (e.g., environment variables).


