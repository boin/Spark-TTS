#!/usr/bin/env python3
# Copyright (c) 2025 SparkAudio
#               2025 Xinsheng Wang (w.xinshawn@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from contextlib import asynccontextmanager
from io import BytesIO
import logging
import os
from pathlib import Path
import platform
import sys
import tempfile
from typing import Literal, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi_cuda_health import setup_cuda_health
import soundfile as sf
import soxr
import torch
import uvicorn

from cli.SparkTTS import SparkTTS
from sparktts.utils.postprocess import eq, loudnorm

sys.path.append(str(Path(os.path.dirname(__file__)).parent.parent))



# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("spark-api")

# 全局模型实例
model = None

def initialize_model(model_dir="pretrained_models/Spark-TTS-0.5B", device=0):
    """加载模型"""
    logger.info(f"正在加载模型: {model_dir}")

    # 根据平台和可用性确定适当的设备
    if platform.system() == "Darwin":
        # macOS with MPS support (Apple Silicon)
        device = torch.device(f"mps:{device}")
        logger.info(f"使用MPS设备: {device}")
    elif torch.cuda.is_available():
        # System with CUDA support
        device = torch.device(f"cuda:{device}")
        logger.info(f"使用CUDA设备: {device}")
    else:
        # Fall back to CPU
        device = torch.device("cpu")
        logger.info("GPU加速不可用，使用CPU")

    return SparkTTS(Path(model_dir), device)

def run_voice_cloning(
    text,
    model,
    prompt_speech,
    prompt_text=None,
    gender=None,
    pitch=None,
    speed=None,
    temperature=0.8,
    top_k=50,
    top_p=0.95,
):
    """执行语音克隆推理并返回音频数据"""
    logger.info("开始语音克隆推理...")

    if prompt_text is not None:
        prompt_text = None if len(prompt_text) <= 1 else prompt_text

    # 执行推理
    with torch.no_grad():
        try:
            wav = model.inference(
                text,
                prompt_speech,
                prompt_text,
                gender=gender,
                pitch=pitch,
                speed=speed,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
            )
            logger.info("推理完成")
            return wav
        except Exception as e:
            logger.error(f"推理过程中发生错误: {str(e)}")
            import traceback
            logger.error(f"错误详情: {traceback.format_exc()}")
            raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    global model
    model_dir = os.environ.get("MODEL_DIR", "pretrained_models/Spark-TTS-0.5B")
    device = int(os.environ.get("DEVICE", "0"))
    logger.info("正在初始化Spark-TTS模型...")
    model = initialize_model(model_dir=model_dir, device=device)
    logger.info("Spark-TTS模型初始化完成")
    yield
    # 关闭时执行
    logger.info("关闭应用...")

# 创建FastAPI应用
app = FastAPI(
    title="Spark-TTS API",
    description="Spark-TTS语音合成API服务",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_cuda_health(app, ready_predicate=lambda: model is not None)

@app.get("/")
async def root():
    """API根路径"""
    return {"message": "欢迎使用Spark-TTS API服务"}

@app.post("/api/infer")
async def infer(
    text: str = Form(...),
    prompt_text: Optional[str]=Form(None),
    prompt_speech: UploadFile = File(...),
    gender:Optional[Literal["male", "female"]] = Form(None),
    pitch:Optional[Literal["very_low", "low", "moderate", "high", "very_high"]] = Form("moderate"),
    speed:Optional[Literal["very_low", "low", "moderate", "high", "very_high"]] = Form("moderate"),
    temperature:Optional[float] = Form(0.8),
    top_k:Optional[int] = Form(50),
    top_p:Optional[float] = Form(0.95),
    postprocess: Optional[bool] = Form(True),
):
    """
    语音克隆API
    
    使用提供的提示语音文件克隆说话风格，生成新的语音。
    
    参数：
        text: 要合成的文本
        prompt_text: 提示文本（可选）
        prompt_speech: 提示语音文件（必需）
        postprocess: 是否进行后处理（默认：True）
    
    返回：
        二进制WAV格式音频数据
    """
    if model is None:
        raise HTTPException(status_code=503, detail="模型未初始化")
    
    try:
        # 处理提示语音
        temp_path = None
        try:
            # 读取上传的音频文件为二进制File字节序列
            audio_bytes = await prompt_speech.read()

            # 使用BytesIO处理二进制数据
            with BytesIO(audio_bytes) as input_buffer:
                # 读取音频数据和采样率
                audio_data, sample_rate = sf.read(input_buffer)
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    temp_path = temp_file.name
                    
                    # 如果采样率不是16kHz，则重采样
                    if sample_rate != 16000:
                        audio_data = soxr.resample(audio_data, sample_rate, 16000)
                        
                    # 直接写入临时文件，16位格式
                    sf.write(temp_path, audio_data, 16000, subtype='PCM_16')
            
            # 执行语音克隆推理
            wav = run_voice_cloning(
                text=text,
                model=model,
                prompt_speech=temp_path,
                prompt_text=prompt_text,
                gender=gender,
                pitch=pitch,
                speed=speed,
                temperature=temperature or 0.8,
                top_k=top_k or 50,
                top_p=top_p or 0.95,
            )
                    
            # 后处理
            if postprocess:
                wav, _ = loudnorm(wav, 16000)
                wav = eq(wav, 16000)
            
            # 超采样至48kHz
            wav = soxr.resample(wav, 16000, 48000)

            # 将音频数据转换为WAV格式的二进制数据
            buffer = BytesIO()
            sf.write(buffer, wav, 48000, format='WAV')
            buffer.seek(0)

            # 返回二进制音频数据
            return Response(
                headers={"Content-Disposition": "attachment; filename=generated.wav"},
                content=buffer.read(),
                media_type="audio/wav"
            )
        finally:
            # 确保临时文件被删除
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
    except Exception as e:
        logger.error(f"语音克隆处理错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音克隆处理错误: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    logger.info(f"启动服务器: {port}")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
