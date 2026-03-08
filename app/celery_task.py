from celery import Celery
from asgiref.sync import async_to_sync
from app.config import Config
from app.mail_config import create_message, mail

# Khởi tạo Celery App kết nối với Redis
c_app = Celery("rag_tasks", broker=Config.BROKER_URL, backend=Config.BACKEND_URL)

@c_app.task()
def send_email(recipients: list[str], subject: str, body: str):
    """Task này sẽ được Celery chạy ngầm"""
    message = create_message(recipients, subject, body)
    # Vì fastapi-mail là thư viện bất đồng bộ (async), ta dùng async_to_sync để chạy trong Celery (đồng bộ)
    async_to_sync(mail.send_message)(message) 
    print(f"Đã gửi email thành công tới {recipients}")