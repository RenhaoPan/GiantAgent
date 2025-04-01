import os
import botpy
from botpy import logging, BotAPI
from botpy.message import Message, C2CMessage, GroupMessage

from botpy.ext.command_util import Commands
from app.config_manager import GlobalConfig  # 修改为绝对导入
from app.core.domain.jmserver import JMServer, init_JMServer
from common import EmailConfig

_log = logging.get_logger()


@Commands("/getpdf")
async def getPDF(api: BotAPI, message: C2CMessage, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    await message._api.post_c2c_message(
        openid=message.author.user_openid,
        msg_type=0,  # 0表示文本类型
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


@Commands("/getpdf")
async def group_getPDF(api: BotAPI, message: GroupMessage, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    # await message._api.post_c2c_message(
    #     openid=message.author.user_openid,
    #     msg_type=0,  # 0表示文本类型
    #     msg_id=message.id,
    #     content="暂不支持pdf，请尝试Email"
    # )
    if params is None:
        return
    param_list = params.split(" ")
    jm_code = param_list[0]
    GlobalConfig.load_config(os.getenv("ENV", "local"))
    file_url = ""
    # 第二种用send发送消息
    try:
        init_JMServer(GlobalConfig.get("runtime_env"))
        JMServer.download_photo(jm_code)
        file_url = f"{JMServer.get_download_path()}{jm_code}.pdf"
    except Exception as e:
        _log.error(f"get jm resource failed", e)
        max_length = 100
        error_message = str(e).replace('\n', ' ').replace('\r', '')[:max_length]
        error_message += "..." if len(str(e)) > max_length else ""
        content = f"下载JM资源失败: {error_message if error_message else '未知错误'}"
        await message._api.post_group_message(group_openid=message.group_openid, msg_type=0, msg_id=message.id,
                                              content=content)

    try:
        uploadMedia = await message._api.post_group_file(
            group_openid=message.group_openid,
            file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
            url=file_url  # 文件Url
        )

        # 资源上传后，会得到Media，用于发送消息
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=7,  # 7表示富媒体类型
            msg_id=message.id,
            media=uploadMedia
        )
    except Exception as e:
        _log.error(f"get jm resource failed", e)
        content = f"发送pdf文件失败:qqbot目前仅支持图片、视频mp4、语音silk类型,请尝试email"
        await message._api.post_group_message(group_openid=message.group_openid, msg_type=0, msg_id=message.id,
                                              content=content)

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
    GlobalConfig.load_config(os.getenv("ENV", "local"))
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
        if email_info is None:
            _log.error("SMTP configuration is missing")
            raise ValueError("SMTP configuration is missing")
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
            content=f"已发送{jm_code}.pdf至{message.author.username}的邮箱"
        )

    return True


@Commands("/email")
async def group_Email(api: BotAPI, message: GroupMessage, params=None):
    _log.info(params)
    # 第一种用reply发送消息
    if params is None:
        return
    param_list = params.split(" ")
    jm_code = param_list[0]
    msg_to = param_list[1]
    GlobalConfig.load_config(os.getenv("ENV", "local"))
    try:
        init_JMServer(GlobalConfig.get("runtime_env"))
        JMServer.download_photo(jm_code)
    except Exception as e:
        _log.error(f"get jm resource failed", e)
        max_length = 100
        error_message = str(e).replace('\n', ' ').replace('\r', '')[:max_length]
        error_message += "..." if len(str(e)) > max_length else ""
        content = f"下载JM资源失败: {error_message if error_message else '未知错误'}"
        await message._api.post_group_message(group_openid=message.group_openid, msg_type=0, msg_id=message.id,
                                              content=content)

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
        await message._api.post_group_message(
            group_openid=message.group_openid,
            msg_type=0,  # 0表示文本类型
            msg_id=message.id,
            content=f"已发送{jm_code}.pdf至您的邮箱"
        )

    return True


class QQBotClient(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_c2c_message_create(self, message: C2CMessage):
        # 注册指令handler
        handlers = [getPDF, Email]
        for handler in handlers:
            if await handler(self.api, message=message):
                return

    async def on_group_at_message_create(self, message: GroupMessage):
        # 注册指令handler
        handlers = [group_getPDF, group_Email]
        for handler in handlers:
            if await handler(self.api, message=message):
                return
