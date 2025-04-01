import sys
import os

# 添加 GiantAgent 目录到 sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # 添加当前目录到sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 添加 GiantAgent 目录到sys.path

import botpy
from config_manager import GlobalConfig
from app.api.qqbot.qqbotclient import QQBotClient

if __name__ == "__main__":
    # 初始化配置（在应用启动时调用）

    GlobalConfig.load_config(os.getenv("ENV", "local"))
    print(f"Loaded config for environment: {GlobalConfig.get('runtime_env')}")  # 添加日志

    intents = botpy.Intents(public_messages=True)
    client = QQBotClient(intents=intents)
    client.run(appid=GlobalConfig.get("qqbot")["appid"], secret=GlobalConfig.get("qqbot")["secret"])