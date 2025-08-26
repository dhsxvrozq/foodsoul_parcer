# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем Firefox и необходимые зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    firefox-esr \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY req.txt .

# Устанавливаем Python-библиотеки
RUN pip install --no-cache-dir -r req.txt

# Копируем проект
COPY . .

# Запуск основного скрипта
CMD ["python", "parcer.py"]
