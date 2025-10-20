import os
import json
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
# Change credentials on line 109
# --- Configuration ---
# You can change these values
MQTT_BROKER = "192.168.1.98"
MQTT_PORT = 1883
MQTT_TOPIC = "/chainloot/persona/yoda/feelings"

# --- Flask App Initialization ---
app = Flask(__name__)
# It's recommended to set a secret key for production apps
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key')
socketio = SocketIO(app, async_mode='eventlet')

# --- In-memory State ---
# This dictionary will hold the most recent emotion data.
# It's used to update new clients as soon as they connect.
current_state = {
    'emotion': 'neutral',
    'image_url': 'https://placehold.co/400x600/667788/FFFFFF?text=Waiting+for+Signal...'
}

# --- Emotion to Image Mapping ---
# Maps the 'dominant_emotion' from the MQTT message to a specific image URL.
# We are using placeholder images here, but you can replace these URLs
# with links to your actual images.
EMOTION_IMAGES = {
    "caring": "https://placehold.co/400x600/FFC0CB/000000?text=Caring",
    "curiosity": "https://placehold.co/400x600/FFD700/000000?text=Curious",
    "realization": "https://placehold.co/400x600/87CEEB/000000?text=Realization",
    "confusion": "https://placehold.co/400x600/E0B0FF/000000?text=Confused",
    "desire": "https://placehold.co/400x600/FF7F50/000000?text=Desire",
    "relief": "https://placehold.co/400x600/98FB98/000000?text=Relieved",
    "annoyance": "https://placehold.co/400x600/FFA07A/000000?text=Annoyed",
    "neutral": "https://placehold.co/400x600/B0C4DE/000000?text=Neutral",
    "disapproval": "https://placehold.co/400x600/A52A2A/FFFFFF?text=Disapproval",
    "approval": "https://placehold.co/400x600/32CD32/FFFFFF?text=Approval",
    "remorse": "https://placehold.co/400x600/778899/FFFFFF?text=Remorse",
    "surprise": "https://placehold.co/400x600/FFFF00/000000?text=Surprised",
    "optimism": "https://placehold.co/400x600/4682B4/FFFFFF?text=Optimistic",
    "pride": "https://placehold.co/400x600/DB7093/FFFFFF?text=Proud",
    "disappointment": "https://placehold.co/400x600/800080/FFFFFF?text=Disappointed",
    "nervousness": "https://placehold.co/400x600/F0E68C/000000?text=Nervous",
    "embarrassment": "https://placehold.co/400x600/FF69B4/000000?text=Embarrassed",
    "admiration": "https://placehold.co/400x600/E6E6FA/000000?text=Admiration",
    "disgust": "https://placehold.co/400x600/556B2F/FFFFFF?text=Disgusted",
    "fear": "https://placehold.co/400x600/2F4F4F/FFFFFF?text=Fearful",
    "gratitude": "https://placehold.co/400x600/DDA0DD/000000?text=Grateful",
    "excitement": "https://placehold.co/400x600/FF4500/FFFFFF?text=Excited",
    "grief": "https://placehold.co/400x600/000080/FFFFFF?text=Grief",
    "sadness": "https://placehold.co/400x600/191970/FFFFFF?text=Sad",
    "anger": "https://placehold.co/400x600/DC143C/FFFFFF?text=Angry",
    "love": "https://placehold.co/400x600/FF1493/FFFFFF?text=Love",
    "joy": "https://placehold.co/400x600/7CFC00/000000?text=Joyful",
    "amusement": "https://placehold.co/400x600/ADFF2F/000000?text=Amused",
    "default": "https://placehold.co/400x600/667788/FFFFFF?text=Unknown+Emotion"
}

# --- MQTT Client Setup ---
def on_connect(client, userdata, flags, rc):
    """Callback function for when the client connects to the MQTT broker."""
    if rc == 0:
        print(f"Successfully connected to MQTT Broker: {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT Broker, return code {rc}\n")

def on_message(client, userdata, msg):
    """Callback function for when a message is received from the subscribed topic."""
    global current_state
    print(f"Received message from topic {msg.topic}: {msg.payload.decode()}")
    try:
        # Decode the payload from bytes to a string and parse as JSON
        data = json.loads(msg.payload.decode('utf-8'))
        
        # Extract the dominant emotion
        dominant_emotion = data.get('dominant_emotion', 'neutral').lower()

        # Get the corresponding image URL, with a fallback to a default image
        image_url = EMOTION_IMAGES.get(dominant_emotion, EMOTION_IMAGES['default'])

        # Update the global state
        current_state['emotion'] = dominant_emotion
        current_state['image_url'] = image_url

        # Emit an event to all connected web clients with the new data
        socketio.emit('emotion_update', {
            'emotion': dominant_emotion,
            'image_url': image_url
        })
        print(f"Emitted update: {dominant_emotion}")

    except json.JSONDecodeError:
        print("Error decoding JSON from MQTT message.")
    except Exception as e:
        print(f"An error occurred in on_message: {e}")

def mqtt_listener():
    """Initializes and runs the MQTT client."""
    # Removed the CallbackAPIVersion argument for broader compatibility
    client = mqtt.Client()
    # --- Add this line for authentication ---
    client.username_pw_set("yoda", "yoda")
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # loop_forever() is a blocking call that handles reconnects automatically.
        client.loop_forever()
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")


# --- Flask Routes ---
@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html', topic=MQTT_TOPIC)

# --- SocketIO Events ---
@socketio.on('connect')
def handle_connect():
    """
    Handles a new client connecting via WebSocket.
    Immediately sends the most recent emotion data to the new client.
    """
    print('Client connected')
    socketio.emit('emotion_update', current_state)


if __name__ == '__main__':
    # We need to run the MQTT client in a separate thread so that it doesn't
    # block the Flask web server.
    print("Starting MQTT listener in a background thread...")
    mqtt_thread = threading.Thread(target=mqtt_listener, daemon=True)
    mqtt_thread.start()

    # The 'eventlet' server is recommended for Flask-SocketIO for performance.
    print("Starting Flask-SocketIO server...")
    # The host='0.0.0.0' makes the server accessible from other devices on your network.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
