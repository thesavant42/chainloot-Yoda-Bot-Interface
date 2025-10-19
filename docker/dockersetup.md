# Docker Setup


To get started, pull the image from GitHub Container Registry:

```
docker pull ghcr.io/rsxdalv/tts-webui:main
```

- Once the image has been pulled it can be started with Docker Compose: 

The ports are 7770 (env:TTS_PORT) for the Gradio backend and 3000 (env:UI_PORT) for the React front end.


```
docker compose up -d
```

The container will take some time to generate the first output while models are downloaded in the background. 

The status of this download can be verified by checking the container logs:

```
docker logs tts-webui
```
### Building the image yourself


If you wish to build your own docker container, you can use the included Dockerfile:

```
docker build -t tts-webui .
```

Please note that the docker-compose needs to be edited to use the image you just built.