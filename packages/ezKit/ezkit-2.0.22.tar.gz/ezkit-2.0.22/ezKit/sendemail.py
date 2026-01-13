from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr
from os import environ
from typing import Optional, TypedDict

import aiosmtplib
from loguru import logger

from . import utils

DEBUG = environ.get("DEBUG")


class TypedSMTP(TypedDict):
    """smtp type"""

    server: str
    port: int
    # tls: bool


class TypedSender(TypedDict):
    """sender type"""

    name: str
    address: str
    password: str


class TypedBody(TypedDict, total=False):
    """body type"""

    content: str
    type: Optional[str]  # "plain", "html", or "file"


def format_parse(s: str) -> str:
    """格式化邮件地址"""
    _name, _addr = parseaddr(s)
    return formataddr((Header(_name, "utf-8").encode(), _addr))


async def sendemail(
    smtp: TypedSMTP,
    sender: TypedSender,
    recipients: str | list[str],
    subject: str,
    body: TypedBody,
    images: Optional[list[dict]] = None,
) -> bool:
    """异步发送邮件"""

    # smtp SMTP信息
    #
    #     server  SMTP地址
    #     port    SMTP端口
    #     tls     是否使用TLS
    #
    # sender 发件人信息
    #
    #     name     发件人名称
    #     address  发件人邮箱地址
    #     password 发件人邮箱密码(SMTP)
    #
    # recipients  收件人(或列表)
    #
    # subject     邮件主题
    #
    # body        邮件主体
    #
    #     content 内容
    #     type    类型 (默认 plain, 或者 file, 或者 html)
    #
    # images 图片列表(可选)
    #
    #     cid  图片CID
    #     path 图片路径

    logger.info("sendemail start")

    try:

        # 邮件主体构建

        if not isinstance(body, dict) or "content" not in body:
            logger.error("body error")
            return False

        message: MIMEMultipart = MIMEMultipart()

        body_content = body["content"]

        if not isinstance(body_content, str):
            logger.error(f"body content error: {body_content}")
            return False

        body_type = body.get("type", "plain")

        if body_type == "file":
            # 从文本文件读取内容
            with open(body_content, "r", encoding="utf-8") as file:
                message.attach(MIMEText(file.read(), "plain", "utf-8"))
        elif body_type == "html":
            # 从HTML文件读取内容
            message = MIMEMultipart("related")
            with open(body_content, "r", encoding="utf-8") as file:
                message.attach(MIMEText(file.read(), "html", "utf-8"))
        else:
            # 纯文本内容
            message.attach(MIMEText(body_content, "plain", "utf-8"))

        # ------------------------------------------------------------------------------------------

        # 设置 SMTP 信息

        smtp_host = smtp.get("server")
        smtp_port = smtp.get("port")
        # smtp_tls = smtp.get("tls", False)

        if not smtp_host or not smtp_port:
            logger.error("SMTP config error")
            return False

        # ------------------------------------------------------------------------------------------

        # 设置发件人信息

        sender_name = sender.get("name")
        sender_address = sender.get("address")
        sender_password = sender.get("password")

        if not sender_name or not sender_address or not sender_password:
            logger.error("Sender config error")
            return False

        message["From"] = formataddr((sender_name, sender_address))

        # ------------------------------------------------------------------------------------------

        # 设置收件人
        if isinstance(recipients, str):
            message["To"] = format_parse(recipients)
        elif isinstance(recipients, list):
            message["To"] = ", ".join([format_parse(r) for r in recipients])
        else:
            logger.error("recipients error")
            return False

        # ------------------------------------------------------------------------------------------

        # 设置邮件主题
        if not isinstance(subject, str):
            logger.error("subject error")
            return False

        message["Subject"] = subject

        # ------------------------------------------------------------------------------------------

        # 处理图片
        if images:
            for image in images:
                try:
                    if utils.check_file_type(image.get("path", ""), "file"):
                        with open(image["path"], "rb") as _image_file:
                            mime_image = MIMEImage(_image_file.read())
                            mime_image.add_header("Content-ID", f"<{image['cid']}>")
                            message.attach(mime_image)
                except Exception as e:
                    logger.exception(e)
                    return False

        # ------------------------------------------------------------------------------------------

        # 使用 aiomail 发送邮件
        async with aiosmtplib.SMTP(hostname=smtp_host, port=smtp_port) as smtp_server:

            # if smtp_tls:
            #     await smtp_server.starttls()

            await smtp_server.login(sender_address, sender_password)
            await smtp_server.sendmail(sender_address, recipients, message.as_string())

        logger.success("sendemail success")

        return True

    except Exception as e:

        # 忽略腾讯邮箱返回的异常
        if e.args == (-1, b"\x00\x00\x00"):
            return True

        logger.error("sendemail error")

        if DEBUG:
            logger.exception(e)
        else:
            logger.error(e)

        return False
