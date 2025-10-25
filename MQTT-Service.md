# MQTT Service Montioring Feedback Notes

  Each container/service stack is meant to now report its' health statistics via MQTT, with a topic for services and a topic for resources.

In practice, however, this is far from consistent. The following services output is all of the currently reported services and sample data for each.

---
## ollama

**/chainloot/system/ollama/resources**

```json
{"timestamp": 1761418216, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
```
 - **Why is everything null?**
**/chainloot/system/ollama/services**

```json
{"timestamp": 1761418216, "service": {"service": "ollama", "available": true, "response_time": 26.92, "error": null}}
```

---
## TTS-WebUI (Speech to text, Text to speech, OpenAI-API)

**/chainloot/system/tts_webui/resources**

```json
{"timestamp": 1761418278, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
```
 - **Why is everything null?**
 - This is not useful, since all it actually shows is a timestamp, not any actual resource utilization.
**/chainloot/system/tts_webui/services**
```json
{"timestamp": 1761418403, "service": {"service": "tts_webui", "available": true, "response_time": 2.97, "error": null}}
```

---
## LocalStack

**/chainloot/system/localstack/resources**
```json
{"timestamp": 1761418465, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
```
 - **Why is everything null?**
 - This is not useful, since all it actually shows is a timestamp, not any actual resource utilization.

**/chainloot/system/localstack/services**
```json
{"timestamp": 1761418496, "service": {"service": "localstack", "available": true, "response_time": 1.56, "error": null}}
```
 - This is not useful, since all it actually shows is a timestamp, not any actual resource utilization.
---
## system 
### The most important in many ways
**/chainloot/system/system/resources**
```json
{"timestamp": 1761418558, "cpu_percent": 0.1, "memory": {"total": 33554579456, "available": 25653116928, "used": 7326588928, "percent": 23.5}, "gpu": {"name": "NVIDIA GeForce RTX 4070", "memory_total": 12282.0, "memory_used": 6253.0, "memory_free": 5760.0, "memory_percent": 50.91190359876242, "temperature": 57.0}, "disk": {"total": 1081101176832, "used": 168562024448, "free": 857546797056, "percent": 16.4}}
```
 - Super useful!!
---
## Chainlit 
**/chainloot/system/chainlit/resources**
```json
{"timestamp": 1761418589, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
```
 - **Why is everything null?**
 - This is not useful, since all it actually shows is a timestamp, not any actual resource utilization.
---
## ProxPi 
### (this is a docker container, not managed as part of the chainloot docker-compose stack)
**/chainloot/system/proxpi/resources**
```json
{"timestamp": 1761418621, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
```
 - **Why is everything null?**
 - This is not useful, since all it actually shows is a timestamp, not any actual resource utilization.

 ---
 ## Nginx Proxy (Not Managed by Chainloot)
 **/chainloot/system/nginx_nginx_proxy_1/resources**
 ```json
{"timestamp": 1761418714, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
 ```
  - **Why is everything null?**
  - This is not useful, since all it actually shows is a timestamp, not any actual resource utilization.
 ---
## ESPHome (Not managed by chainloot)
**/chainloot/system/esphome/resources**
```json
{"timestamp": 1761418839, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
```
---
## QDrant (Not part of chainloot or managed by chainloot)
**/chainloot/system/qdrant/resources**
```json
{"timestamp": 1761418870, "cpu_percent": null, "memory_usage": null, "memory_limit": null, "memory_percent": null, "status": null}
```

 - This is not useful, since all it actually shows is a timestamp, not any actual resource utilization.
---
## LM Studio (?!)
**/chainloot/system/lm_studio/services**
 - **How does this exist?!** 
    - LM Studio is *not* a Docker container, 
    - I have not configured it to use MQTT. 
 - Is this hallucinated?
```json
{"timestamp": 1761418963, "service": {"service": "lm_studio", "available": true, "response_time": 3.39, "error": null}}
```
---
## PostgreSQL
**/chainloot/system/postgres/services**
```json
{"timestamp": 1761418994, "service": {"service": "postgres", "available": false, "response_time": 3.51, "error": "Server disconnected"}}
```
- This could be a lot more useful, but at least it's something?

---

## Feedback

    - Based upon the number of NULL value responses, and the mystery lm_studio entry, I have some doubts as to how accutate these reportings are
---

**Q: Is it *possible* to get the stats that are currently printing `NULL`?**
**A:**
Source(s):
Notes:

**Q: Why are they reporting 'NULL' at all?**
 - Is this a problem with the script?
**A:**
Source(s):
Notes:

**Q:** 
**A:**
Source(s):
Notes:

Overall, as a proof of concept the MQTT project has proven that it's extremely useful, and worth the effort to fix any otustanding bugs. 

One recommended improvement miight be to parse out the services so that the non-chainloot services are grouped together, apart from the chainloot managed services in the Topic tree. 