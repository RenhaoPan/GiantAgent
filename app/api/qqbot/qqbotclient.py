import os
import botpy
from botpy import logging, BotAPI
from botpy.message import Message, C2CMessage

from botpy.ext.command_util import Commands
from ...config_manager import GlobalConfig
from ...core.domain.jmserver import JMServer, init_JMServer
from common import EmailConfig

_log = logging.get_logger()

@Commands("/getpdf")
async def getPDF(api: BotAPI, message: C2CMessage, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    await message._api.post_c2c_message(
        openid=message.author.user_openid,
        msg_type=0, # 0表示文本类型
        msg_id=message.id,
        content="暂不支持pdf，请尝试Email"
    )
    # 第二种用send发送消息
    # file_url = 'http://8.133.196.106:9090/jmoss/422866.pdf'  # 这里需要填写上传的资源Url
    # uploadMedia = await message._api.post_c2c_file(
    #     openid=message.author.user_openid,
    #     file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
    #     url=file_url  # 文件Url
    # )
    #
    # # 资源上传后，会得到Media，用于发送消息
    # await message._api.post_c2c_message(
    #     openid=message.author.user_openid,
    #     msg_type=7,  # 7表示富媒体类型
    #     msg_id=message.id,
    #     media=uploadMedia
    # )

    return True

@Commands("/email")
async def Email(api: BotAPI, message: C2CMessage, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    if params is None:
        return
    param_list = params.split(" ")
    jm_code = param_list[0]
    msg_to = param_list[1]
    GlobalConfig.load_config(os.getenv('env', 'local'))
    try:
        await message._api.post_c2c_message(
            openid=message.author.user_openid,
            msg_type=0,  # 0表示文本类型
            msg_id=message.id,
            content=f"正在下载资源 {jm_code}，请稍后"
        )
        init_JMServer(GlobalConfig.get("runtime_env"))
        JMServer.download_photo(jm_code)
    except Exception as e:
        _log.error(f"get jm resource failed", e)

    email_glag = False
    try:
        email_info = GlobalConfig.get('smtp')
        econfig = EmailConfig(email_info['msg_from'], msg_to, email_info['password'])
        qq_email_postman = econfig.create_email_postman()
        email_glag = qq_email_postman.send(text="jmcomic finished !!!", subject=f"jmcomic {jm_code}",
                                     filepath=f"{email_info['file_path']}{jm_code}.pdf")
    except Exception as e:
        _log.error(f"Send email failed", e)
    if email_glag is True:
        await message._api.post_c2c_message(
            openid=message.author.user_openid,
            msg_type=0,  # 0表示文本类型
            msg_id=message.id,
            content=f"以发送至您的邮箱"
        )

    return True
class QQBotClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_c2c_message_create(self, message: C2CMessage):
        # 注册指令handler
        hadlers = [getPDF, Email]
        for handler in hadlers:
            if await handler(self.api, message=message):
                return
