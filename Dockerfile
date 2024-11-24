FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    vim \
    net-tools \
    iputils-ping \
    curl \ 
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python packages
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# 모델 파일을 미리 다운로드하여 캐시에 저장
RUN mkdir -p /root/.u2net && \
    curl -L -o /root/.u2net/u2net.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx

RUN python3 --version

# Set the working directory
WORKDIR /workspace
COPY . /workspace

# CMD ["tail", "-f", "/dev/null"]