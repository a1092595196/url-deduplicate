FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

# 使用 Gunicorn 运行应用（生产环境推荐）
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
