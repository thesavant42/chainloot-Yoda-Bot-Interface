# Python 3.10 w/ Nvidia Cuda
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04 AS env_base

# Install Pre-reqs
RUN apt-get update && apt-get install --no-install-recommends -y \
    git vim nano build-essential python3-dev python3-venv python3-pip gcc g++ ffmpeg pkg-config \
    libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libavfilter-dev libswscale-dev libswresample-dev jq

ENV NODE_VERSION=22.9.0
RUN apt-get update && apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version

# Install uv
# ADD --chmod=755 https://astral.sh/uv/install.sh /install.sh
# RUN /install.sh && rm /install.sh

# Define PyTorch version
ENV TORCH_VERSION=2.7.0

ENV PATH="/root/.cargo/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel

# Copy the pip configuration file
COPY ../pip.conf /etc/pip.conf
# add xformers?
RUN pip install setuptools torch==$TORCH_VERSION torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128

# Set working directory
WORKDIR /app

# Clone the repo
RUN git clone https://github.com/rsxdalv/tts-webui.git /app/tts-webui

# Set working directory to the cloned repo
WORKDIR /app/tts-webui

# Copy requirements files
COPY tts-webui/requirements-tts-webui.txt /app/tts-webui/requirements-tts-webui.txt 
# Install all requirements (torch already installed above)
RUN pip3 install -r /app/tts-webui/requirements-tts-webui.txt

# Copy TTS-WebUI config with auto-start enabled
COPY tts-webui/tts-webui-config.json /app/tts-webui/config.json

# Ensure extension_openai_tts_api auto_start is set to true if not present
RUN jq '.extension_openai_tts_api = (.extension_openai_tts_api // {}) | .extension_openai_tts_api.auto_start = (.extension_openai_tts_api.auto_start // true)' /app/tts-webui/config.json > /tmp/config.json && mv /tmp/config.json /app/tts-webui/config.json

# add postgres & run setup
# Build the React UI
RUN cd react-ui && npm install && npm run build

# Run the server
CMD python3 server.py --docker
