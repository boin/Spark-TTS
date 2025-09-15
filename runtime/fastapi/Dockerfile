FROM pytorch/pytorch:2.5.1-cuda12.1-cudnn9-devel

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    PYTHONPATH=/app \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata git git-lfs libsndfile1 curl \
    && rm -rf /var/lib/apt/lists/*

# 创建继承式 venv（复用 base 里的 torch 等）
RUN python -m venv --system-site-packages /opt/appenv
ENV VIRTUAL_ENV=/opt/appenv
ENV PATH="/opt/appenv/bin:${PATH}"

RUN --mount=type=bind,source=requirements.txt,target=/tmp/requirements.txt \
    --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt \
    && pip install fastapi uvicorn python-multipart pyloudnorm

WORKDIR /app
COPY runtime/fastapi/server.py /app/
COPY cli /app/cli
COPY sparktts /app/sparktts

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "server.py"]