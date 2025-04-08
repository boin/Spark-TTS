FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata git git-lfs libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    pip3 install --no-cache-dir -r /tmp/requirements.txt \
    && pip3 install fastapi uvicorn python-multipart pyloudnorm

WORKDIR /app
COPY ./runtime/fastapi/server.py /app/
COPY ./cli /app/cli
COPY ./sparktts /app/sparktts

# 模型目录将通过挂载提供
VOLUME ["/app/pretrained_models"]

# 自动下载模型（如果挂载卷中不存在）
RUN if [ ! -f /app/pretrained_models/Spark-TTS-0.5B/config.yaml ]; then \
        git clone https://huggingface.co/SparkAudio/Spark-TTS-0.5B /app/pretrained_models/Spark-TTS-0.5B; \
    fi

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# 启动服务
CMD ["python", "server.py"]
