FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y \
    tzdata git git-lfs \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && pip3 install torchvision torchaudio

WORKDIR /app
COPY . .

VOLUME ["/app/pretrained_models"]

RUN if [ ! -f /app/pretrained_models/Spark-TTS-0.5B/config.yaml ]; then \
        git clone https://huggingface.co/SparkAudio/Spark-TTS-0.5B /app/pretrained_models/Spark-TTS-0.5B; \
    fi

CMD ["python", "webui.py"]