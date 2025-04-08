#!/bin/bash
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

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 获取项目根目录的绝对路径
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# 设置环境变量
export MODEL_DIR=${MODEL_DIR:-"${PROJECT_ROOT}/pretrained_models/Spark-TTS-0.5B"}
export DEVICE=${DEVICE:-0}
export PORT=${PORT:-8000}
export PYTHONPATH=${PYTHONPATH:-"${PROJECT_ROOT}"}

echo "启动Spark-TTS FastAPI服务器..."
echo "模型目录: $MODEL_DIR"
echo "设备ID: $DEVICE"
echo "项目根目录: $PROJECT_ROOT"

# 启动服务器
cd "${SCRIPT_DIR}" && python server.py "$@"
