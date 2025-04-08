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

import requests
import argparse
import os
import time
import soundfile as sf
import pyloudnorm as pyln
from io import BytesIO

def test_health(base_url):
    """测试健康检查端点"""
    url = f"{base_url}/health"
    print(f"测试健康检查端点: {url}")
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ 健康检查成功")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败，状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 健康检查请求异常: {str(e)}")
        return False

def test_voice_clone(base_url, text, output_file, prompt_text=None, prompt_speech=None):
    """测试语音克隆端点"""
    url = f"{base_url}/api/infer"
    print(f"测试语音克隆端点: {url}")
    print(f"文本: {text}")
    
    # 准备表单数据
    data = {
        "text": text,
        "postprocess": "true"
    }
    
    if prompt_text:
        data["prompt_text"] = prompt_text
        print(f"提示文本: {prompt_text}")
    
    files = {}
    if prompt_speech and os.path.exists(prompt_speech):
        # 正确打开文件作为二进制文件对象
        files["prompt_speech"] = (os.path.basename(prompt_speech), open(prompt_speech, "rb"), "audio/wav")
        print(f"提示语音: {prompt_speech}")
    else:
        print("错误: 提示语音文件不存在或未指定")
        return False
    
    try:
        start_time = time.time()
        response = requests.post(url, data=data, files=files)
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ 语音克隆成功，耗时: {end_time - start_time:.2f}秒")
            
            # 保存音频文件
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"音频已保存至: {output_file}")
            
            # 获取音频信息
            audio_data = BytesIO(response.content)
            audio, sample_rate = sf.read(audio_data)
            duration = len(audio) / sample_rate
            
            # 计算平均响度
            meter = pyln.Meter(sample_rate)
            loudness = meter.integrated_loudness(audio)
            
            print(f"音频长度: {duration:.2f}秒，采样率: {sample_rate}Hz, 平均响度: {loudness:.2f} LUFS")
            
            return True
        else:
            print(f"❌ 语音克隆失败，状态码: {response.status_code}")
            print(f"响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 语音克隆请求异常: {str(e)}")
        return False
    finally:
        # 关闭文件句柄
        for file_tuple in files.values():
            if hasattr(file_tuple[1], 'close'):
                file_tuple[1].close()

def main():
    parser = argparse.ArgumentParser(description="Spark-TTS API测试工具")
    parser.add_argument("--url", default="http://localhost:8000", help="API服务器URL")
    parser.add_argument("--text", default="这是一段用于测试的文本，希望能够合成自然流畅的语音。", help="要合成的文本")
    parser.add_argument("--output", default="output.wav", help="输出音频文件路径")
    parser.add_argument("--prompt-text", help="提示文本")
    parser.add_argument("--prompt-speech", help="提示语音文件路径")
    
    args = parser.parse_args()
    
    # 设置默认提示语音文件路径
    if not args.prompt_speech:
        args.prompt_speech = '../../example/prompt_audio.wav'
        args.prompt_text = '吃燕窝就选燕之屋，本节目由26年专注高品质燕窝的燕之屋冠名播出。豆奶牛奶换着喝，营养更均衡，本节目由豆本豆豆奶特约播出。'
    
    # 确保提示语音文件存在
    if args.prompt_speech and not os.path.exists(args.prompt_speech):
        print(f"错误: 提示语音文件不存在: {args.prompt_speech}")
        return
    
    # 如果指定了提示文本，输出提示
    if args.prompt_text:
        print(f"使用提示文本: {args.prompt_text}")

    # 创建输出目录
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 测试健康检查
    if not test_health(args.url):
        print("健康检查失败，终止测试")
        return
    
    # 测试语音克隆
    test_voice_clone(
        args.url, 
        args.text, 
        args.output,
        prompt_text=args.prompt_text,
        prompt_speech=args.prompt_speech
    )

if __name__ == "__main__":
    main()
