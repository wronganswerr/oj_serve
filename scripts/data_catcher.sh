#!/bin/bash

activate_bin="/root/miniconda3/bin/activate"
env="serve"

# 激活特定的 conda 环境
source "${activate_bin}" "${env}"


# 切换到工作目录
cd /root/oj_serve || { echo "切换目录失败"; exit 1; }

# 执行 Python 脚本
python -m app.serve.user_data_catcher

# 0 * * * * /root/oj_serve/scripts/data_catcher.sh >> /root/oj_serve/runtime/catcher_data/user_data_catcher.log 2>&1