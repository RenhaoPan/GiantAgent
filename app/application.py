import botpy
import argparse
from config_manager import GlobalConfig
from app.api.qqbot.qqbotclient import QQBotClient


if __name__ == "__main__":
    # 初始化配置（在应用启动时调用）
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", help="运行环境", choices=["local", "remote"], default="local")
    args = parser.parse_args()
    GlobalConfig.load_config(args.env)

    intents = botpy.Intents(public_messages=True)
    client = QQBotClient(intents=intents)
    client.run(appid=GlobalConfig.get("qqbot")["appid"], secret=GlobalConfig.get("qqbot")["secret"])
