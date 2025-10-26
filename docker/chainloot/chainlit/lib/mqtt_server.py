from mqtt_mcp import MQTTMCP

mcp = MQTTMCP()

if __name__ == "__main__":
    mcp.run(transport="http", port=8100)  # Use port 8100 to avoid conflicts