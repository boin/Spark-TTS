# Spark-TTS FastAPI 服务器

Spark-TTS FastAPI 服务器提供了一个简单高效的 API 接口，用于语音克隆功能。

## 实现特点

1. 单文件实现 (server.py)，包含所有核心逻辑
2. Docker 部署，基于 PyTorch 官方镜像
3. 使用 bind mount 优化依赖安装，支持自动下载模型
4. 单一端点 `/api/infer`，专注于语音克隆功能
5. 使用 lifespan 事件处理器初始化模型
6. 直接在内存中处理音频数据，不写入本地文件
7. 支持音频后处理和超采样至 48kHz
8. 使用外部命名卷挂载模型目录

## API 接口

### `/api/infer` (POST)

语音克隆 API 端点，使用提供的提示语音文件克隆说话风格，生成新的语音。

**参数：**
- `text`: 要合成的文本 (必填)
- `prompt_text`: 提示文本 (可选)
- `prompt_speech`: 提示语音文件，WAV 格式 (必填，用于语音克隆)
- `postprocess`: 是否进行后处理，默认为 True (可选)

**返回：**
- 二进制 WAV 格式音频数据 (48kHz)

## 部署方式

### 使用 Docker Compose

1. 确保已安装 Docker 和 Docker Compose
2. 在 `runtime/fastapi` 目录下运行：
   ```bash
   docker-compose up -d
   ```

### 本地运行

1. 确保已安装所有依赖（见项目根目录的 `requirements.txt`）
2. 在 `runtime/fastapi` 目录下运行：
   ```bash
   ./run.sh
   ```

## 测试 API

可以使用提供的测试脚本来测试 API：

```bash
# 使用默认参数测试
python test_api.py

# 指定文本和提示语音
python test_api.py --text "这是一段测试文本" --prompt-speech /path/to/audio.wav

# 指定输出文件
python test_api.py --output result.wav
```

## 环境变量

服务器支持以下环境变量：

- `MODEL_DIR`: 模型目录，默认为 `pretrained_models/Spark-TTS-0.5B`
- `DEVICE`: GPU 设备 ID，默认为 0
- `PORT`: 服务器端口，默认为 8000
- `PYTHONPATH`: Python 路径，默认为项目根目录

## Docker 镜像构建

```bash
# 在项目根目录下运行
docker build -t spark-tts-api -f runtime/fastapi/Dockerfile .
```
