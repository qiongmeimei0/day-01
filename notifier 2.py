import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage

from config import (
    EMAIL_ENABLED,
    EMAIL_FROM,
    EMAIL_PASSWORD,
    EMAIL_SMTP_HOST,
    EMAIL_SMTP_PORT,
    EMAIL_TO,
)


def send_notification(subject, body):
    """发送通知；失败时只打印错误，不中断交易程序。"""
    if not EMAIL_ENABLED:
        print("邮件通知未启用:", subject)
        return False
    if not all((EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO)):
        print("邮件配置不完整，跳过通知:", subject)
        return False

    message = EmailMessage()
    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO
    message["Subject"] = f"[day-01] {subject}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    message.set_content(f"时间：{now}\n\n{body}")

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, context=context, timeout=20
        ) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
            smtp.send_message(message)
        print("邮件通知已发送:", subject)
        return True
    except Exception as exc:
        print("邮件发送失败:", exc)
        return False

