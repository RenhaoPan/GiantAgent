# GiantAgent
GiantAgent是Giant的私人Agent智能体

## 项目结构
### app/
- **api/**: 存放API模块。
    - **qqbot/**: 
      - **qqbotclient.py**: QQBot客户端
- **core/**: 存放核心模块。
  - **domain/**:
    - **jmserver.py**: JMServer模块 
- **resources/**: 存放配置文件
  - **remotejmopt.yml**: 远程JM配置文件。
  - **localjmopt.yml**: 本地JM配置文件。
- **application.py**: 主程序入口。
- **config_manager.py**: 配置读取文件

## QQBot
一、文档参考 https://bot.q.qq.com/wiki/

二、python SDK https://github.com/tencent-connect/botpy/tree/master
### 部分第三方库安装

因为JMServer会被识别为有害库建议从源代码库安装
pip install git+https://github.com/hect0x7/JMComic-Crawler-Python


pip install -r requirements.txt