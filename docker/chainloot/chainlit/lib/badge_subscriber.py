#!/usr/bin/env python3
# The issue was that badge.write_svg() doesn't actually write the file
#  directly—you need to convert the Badge object to a string with 
# str(badge) and write it manually. The fix aligns with how the
#  simple_badge.py example in the repo does it.

"""
Badge Subscriber Script
Subscribes to MQTT system stats and generates SVG badges
"""

import json
import os
import sys
import logging
import paho.mqtt.client as mqtt
import anybadge

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/badge_subscriber.log')
    ]
)
logger = logging.getLogger(__name__)

def get_color(value, yellow_threshold, red_threshold):
    """Determine badge color based on value thresholds"""
    if value < yellow_threshold:
        return "#4CAF50"  # green
    elif value < red_threshold:
        return "#FFEB3B"  # yellow
    else:
        return "#F44336"  # red

def on_connect(client, userdata, flags, rc):
    logger.info(f"Badge subscriber connected to MQTT with result code {rc}")
    if rc != 0:
        logger.error(f"MQTT connection failed with code {rc}")
        return
    # Subscribe to system stats topics
    topics = [
        "/chainloot/system/cpu/percent",
        "/chainloot/system/memory/percent",
        "/chainloot/system/gpu/gpu_0/memory_util_percent",
        "/chainloot/system/gpu/gpu_0/temperature"
    ]
    for topic in topics:
        client.subscribe(topic)
        logger.info(f"Subscribed to topic: {topic}")

def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        value = float(msg.payload.decode('utf-8'))
        
        logger.debug(f"Received MQTT message - Topic: {topic}, Value: {value}")
        
        # Determine badge label and format
        if topic == "/chainloot/system/cpu/percent":
            label = "CPU"
            text = f"{value:.1f}%"
            color = get_color(value, 50, 80)
        elif topic == "/chainloot/system/memory/percent":
            label = "MEM"
            text = f"{value:.1f}%"
            color = get_color(value, 50, 80)
        elif topic == "/chainloot/system/gpu/gpu_0/memory_util_percent":
            label = "GPU MEM"
            text = f"{value:.1f}%"
            color = get_color(value, 50, 80)
        elif topic == "/chainloot/system/gpu/gpu_0/temperature":
            label = "GPU TEMP"
            text = f"{value:.0f}°C"
            color = get_color(value, 60, 80)
        else:
            logger.warning(f"Unknown topic received: {topic}")
            return  # Unknown topic
        
        # Generate badge
        badge = anybadge.Badge(label, text, default_color=color)
        
        # Ensure badges directory exists
        os.makedirs("/app/public/badges", exist_ok=True)
        
        # Save badge
        filename = f"{label.lower().replace(' ', '_')}.svg"
        filepath = f"/app/public/badges/{filename}"
        
        # Write SVG content to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(badge))
        
        logger.info(f"Generated badge: {filepath}")
        
    except Exception as e:
        logger.error(f"Error generating badge for {msg.topic}: {e}", exc_info=True)

def main():
    mqtt_host = os.getenv("MQTT_HOST", "192.168.1.98")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    
    logger.info(f"Badge subscriber starting... connecting to {mqtt_host}:{mqtt_port}")
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(mqtt_host, mqtt_port, 60)
        logger.info(f"Connected to MQTT broker at {mqtt_host}:{mqtt_port}")
        client.loop_forever()
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()