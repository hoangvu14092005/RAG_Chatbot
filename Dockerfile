# Sử dụng môi trường Python gọn nhẹ
FROM python:3.11-slim

# Cài đặt một số công cụ hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc mặc định trong container
WORKDIR /app

# Copy file danh sách thư viện vào trước
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn của bạn vào container
COPY . .

# Chỉ định port mà FastAPI sẽ chạy
EXPOSE 8000

# Lệnh để khởi động ứng dụng
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]