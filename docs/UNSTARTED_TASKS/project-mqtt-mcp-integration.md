# MQTT MCP Server Integration Guide

## Overview
This document outlines the steps to integrate the `mqtt-mcp` server into the Chainloot Yoda Bot Interface, enabling Master Yoda and other personas to read real-time MQTT data including emotions, system resources, and container status.

The mqtt-mcp server will be launched **on-demand** by Chainlit's MCP manager when tool discov22ery identifies MQTT-related requests, following the same pattern as all other MCP servers in the system.

## Prerequisites
- Chainloot application running with Mosquitto MQTT broker
- Administrative access to modify configuration files
- Existing MQTT configuration in `chainlit.env` (already present)

## ~~Phase 1: Container Integration~~

### 1.1 Install mqtt-mcp in Chainlit Container
- [x] **Add mqtt-mcp to Dockerfile UV installations**
  - [x] Open `docker/chainloot/chainlit/chainlit.Dockerfile`
  - [x] Locate the section with `uv tool install` commands
  - [x] Add `uv tool install mqtt-mcp` to the existing RUN command
  - [x] This installs mqtt-mcp as a UV tool, making `uvx mqtt-mcp` available

### ~~1.2 Update MCP Servers Configuration~~  
- [x] **Add MQTT server to `mcp_servers.json`**
  - [x] Open `docker/chainloot/chainlit/config/mcp_servers.json`
  - [x] Add new server configuration:
    ```json
    "mqtt": {
      "command": "uvx", 
      "args": ["mqtt-mcp"],
      "env": {
        "MQTT_MCP_MQTT__HOST": "${MQTT_BROKER}",
        "MQTT_MCP_MQTT__PORT": "${MQTT_PORT}", 
        "MQTT_MCP_MQTT__USERNAME": "${MQTT_USERNAME}",
        "MQTT_MCP_MQTT__PASSWORD": "${MQTT_PASSWORD}"
      },
      "description": "MQTT broker communication for real-time data access"
    }
    ```

### ~~1.3 Environment Variables Setup~~
- [x] **Verify existing MQTT variables in chainlit.env**
  - [x] Confirm `docker/chainloot/chainlit/chainlit.env` already contains:
    ```bash
    # MQTT Configuration for Emotion Publishing
    MQTT_BROKER=mosquitto
    MQTT_PORT=1883
    MQTT_USERNAME=yoda
    MQTT_PASSWORD=yoda
    ```
  - [x] **No changes needed** - existing variables will be used by mqtt-mcp server

### 1.4 Container Rebuild
- [x] **Rebuild Chainlit container with mqtt-mcp**
  - [x] From workspace root: `docker-compose -f docker/chainloot/docker-compose.yml build chainlit`
  - [x] Restart containers: `docker-compose -f docker/chainloot/docker-compose.yml up -d`
  - [ ] Verify mqtt-mcp is available in container: `docker exec chainloot-chainlit-1 uvx mqtt-mcp --help`
### 2.3 Create MQTT MCP Configuration on Alfred

- [ ] **Test MQTT connectivity via Inspector**
  - [ ] Use inspector to call `receive_message` tool
  - [ ] Test with parameters:
    ```json
    {
      "topic": "/chainloot/persona/yoda/feelings",
      "timeout": 10
    }
    ```
  - [ ] Verify successful connection to Mosquitto broker on Alfred
  - [ ] Confirm authentication works with yoda:yoda credentials
  - [ ] **Expected result**: Should receive JSON data from topic or timeout message


## Phase 3: Application Integration

### 3.1 MCP Tool Processor Updates
- [ ] **Review current MCP integration**
  - [ ] Examine `lib/mcp_tool_processor.py`
  - [ ] Identify how new MQTT tools will be discovered
  - [ ] Verify automatic tool detection works with dynamic MCP manager

### 3.2 Enable MQTT Topic Reading
- [ ] **Test basic MQTT reading capability**
  - [ ] Start all containers: `docker-compose -f docker/chainloot/docker-compose.yml up -d`
  - [ ] Verify MQTT MCP server is available in MCP tool list
  - [ ] Test bot query: "What's my current emotional state?"
  - [ ] Verify response from `/chainloot/persona/yoda/feelings` topic

### 3.3 Define Common MQTT Queries
- [ ] **Create helper functions or prompts for common operations**
  - [ ] Emotional state checking: `/chainloot/persona/{persona}/feelings`
  - [ ] System resource monitoring: `/chainloot/system/+/resources`
  - [ ] Container status: `/chainloot/system/+/services`
  - [ ] Persona status: `/chainloot/persona/{persona}/status`

## Phase 4: Testing & Validation

### 4.1 Functional Testing
- [ ] **Test persona emotion reading**
  - [ ] Start conversation with Yoda
  - [ ] Ask "How are you feeling right now?"
  - [ ] Verify MQTT MCP retrieves data from feelings topic
  - [ ] Confirm JSON parsing and human-readable response

- [ ] **Test system monitoring**
  - [ ] Ask "What's the system resource usage?"
  - [ ] Verify CPU, memory, disk usage retrieval
  - [ ] Test container-specific queries

- [ ] **Test real-time capabilities**
  - [ ] Generate emotion change (send message that triggers sentiment analysis)
  - [ ] Ask for current emotion immediately after
  - [ ] Verify latest data is retrieved

### 4.2 Error Handling Testing
- [ ] **Test connection failures**
  - [ ] Stop Mosquitto broker temporarily
  - [ ] Verify graceful error handling in MQTT MCP
  - [ ] Test reconnection when broker returns

- [ ] **Test invalid topic queries**
  - [ ] Request non-existent topics
  - [ ] Verify appropriate error messages
  - [ ] Test timeout scenarios

### 4.3 Performance Testing
- [ ] **Test response times**
  - [ ] Measure MQTT query latency
  - [ ] Test with multiple concurrent queries
  - [ ] Verify no impact on normal conversation flow

## Phase 5: Documentation & Rollout

### 5.1 User Documentation
- [ ] **Update bot capabilities documentation**
  - [ ] Document new MQTT reading capabilities
  - [ ] Provide example queries users can try
  - [ ] List available topic patterns

### 5.2 Operational Documentation
- [ ] **Create troubleshooting guide**
  - [ ] Common MQTT connection issues
  - [ ] MCP server debugging steps
  - [ ] Log locations and monitoring

### 5.3 System Integration Validation
- [ ] **Verify all containers start correctly**
  - [ ] Test full system restart
  - [ ] Confirm MQTT MCP initializes properly
  - [ ] Validate persistent configuration

## Success Criteria
Upon completion, Master Yoda and other personas should be able to:
- ✅ Read their current emotional state from MQTT
- ✅ Check system resource usage in real-time
- ✅ Monitor container health and status
- ✅ Access any published MQTT topic data through natural language queries
- ✅ Receive human-readable responses from structured MQTT data

## Rollback Plan
If issues occur during integration:
- [ ] Remove MQTT server entry from `mcp_servers.json`
- [ ] Restart Chainlit container to reload configuration
- [ ] System returns to previous functionality

## Expected Timeline
- **Phase 1-2**: 30-60 minutes (configuration and testing)
- **Phase 3**: 15-30 minutes (integration verification)
- **Phase 4**: 30-45 minutes (comprehensive testing)
- **Phase 5**: 15 minutes (documentation updates)

**Total estimated time**: 1.5-2.5 hours

## Key Configuration Files Modified
1. `docker/chainloot/chainlit/chainlit.Dockerfile` - Add mqtt-mcp to UV tool installations
2. `docker/chainloot/chainlit/config/mcp_servers.json` - Add MQTT server entry
3. `docker/chainloot/chainlit/chainlit.env` - **Already contains MQTT variables** (no changes needed)

## Deployment Architecture
- **MQTT MCP Server**: Runs inside Chainlit Docker container as MCP subprocess
- **Docker Host**: Alfred at `192.168.1.98`
- **Mosquitto Broker**: Docker container on Alfred, connected via Docker network
- **Chainlit Application**: Docker container on Alfred, spawns MQTT MCP server as needed
- **MCP Communication**: Chainlit container → Internal MCP subprocess → Docker network → Mosquitto container

## MQTT Topics Available for Reading
Based on current system architecture:
- `/chainloot/persona/{persona}/feelings` - Emotional state data
- `/chainloot/persona/{persona}/status` - Online/idle/offline status
- `/chainloot/system/system/resources` - System-wide resource usage
- `/chainloot/system/{container}/resources` - Per-container resource usage
- `/chainloot/system/{service}/services` - Service availability status

## Authentication Details
- **MQTT MCP to Mosquitto**: 
  - **Connection**: Chainlit container → `mosquitto:1883` (Docker network)
  - **Username**: `yoda` (from existing MQTT_USERNAME)
  - **Password**: `yoda` (from existing MQTT_PASSWORD)
  - **Protocol**: MQTT v5.0 with username/password authentication
  - **Connection**: Non-SSL, Docker container-to-container network
- **Chainlit to MQTT MCP**:
  - **Connection**: Internal subprocess communication within Chainlit container
  - **Protocol**: MCP stdio transport (process communication)
  - **Authentication**: None required (internal process)
  - **Note**: MQTT MCP runs as subprocess spawned by Chainlit's MCP manager