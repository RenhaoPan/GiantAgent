import smtplib
from email.mime.application import MIMEApplication as emailApp
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException
from typing import List

from common import Union, Optional


class EmailConfig:

    def __init__(self,
                 msg_from: str,
                 msg_to: str,
                 pwd: str):
        self.msg_from = msg_from
        self.msg_to = msg_to
        self.pwd = pwd

    def create_email_postman(self):
        return QQEmailPostman(self)


class QQEmailPostman:

    def __init__(self, conf: EmailConfig):
        self.email_config = conf

    def send(self,
             text: str,
             subject: str,
             attachments: Optional[Union[str, List[str]]] = None) -> bool:
        return self.send_email(self.email_config, text, subject, attachments)

    @staticmethod
    def send_email(conf: EmailConfig,
                   text: str,
                   subject: str = None,
                   attachments: Optional[Union[str, List[str]]] = None) -> Union[bool, SMTPException]:
        if subject is None:
            subject = text[:10]

        msg = MIMEMultipart()
        text = MIMEText(text)
        msg.attach(text)

        msg['Subject'] = subject
        msg['From'] = conf.msg_from
        msg['To'] = conf.msg_to

        if attachments is not None:
            attachment_list = []
        elif isinstance(attachments, str):
            attachment_list = [attachments]
        else:
            attachment_list = attachments

        for filepath in attachment_list:
            with open(filepath, 'rb') as f:
                doc_apart = emailApp(f.read())
            doc_apart.add_header('Content-Disposition', 'attachment', filename=filepath)
            msg.attach(doc_apart)

        try:
            s = smtplib.SMTP_SSL("smtp.qq.com", 465)
            s.login(conf.msg_from, conf.pwd)
            s.sendmail(conf.msg_from, conf.msg_to, msg.as_string())
            return True
        except smtplib.SMTPException as e:
            return e
