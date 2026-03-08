from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.config import Config

mail_config = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM=Config.MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER=Config.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

mail = FastMail(config=mail_config)

def create_message(recipients: list[str], subject: str, body: str):
    return MessageSchema(
        recipients=recipients, subject=subject, body=body, subtype=MessageType.html
    )