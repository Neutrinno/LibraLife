FROM python:3.12-slim

WORKDIR /app

# PYTHONPATH указывает на /app, где окажется ваша папка app/
ENV PYTHONPATH=/app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем контекст (в compose context=search_service) прямо в /app
COPY . /app

EXPOSE 8082

# По-умолчанию запускаем uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8082"]