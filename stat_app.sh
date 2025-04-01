#!/bin/bash
# 设置conda环境
conda activate giantagent

# 设置环境变量
export ENV=remote

# 使用nohup启动应用程序
nohup python app/application.py &

