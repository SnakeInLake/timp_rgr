FROM python:3.12-slim
ENV PYTHONUNBUFFERED 1
WORKDIR /app

# Предполагается, что requirements.txt лежит в папке app/
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]