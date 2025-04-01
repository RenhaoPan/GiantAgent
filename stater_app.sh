#!/bin/bash

# 初始化 Conda
source ~/.bashrc

# 设置conda环境
conda activate giantagent

# 设置环境变量
export ENV=remote

# 删除botpy.log和nohup.out文件
rm -f botpy.log nohup.out

# 使用nohup启动应用程序
nohup python app/application.py &

