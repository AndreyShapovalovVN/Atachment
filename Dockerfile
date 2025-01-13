# Базовый образ с Python и установленными зависимостями
FROM tiangolo/uwsgi-nginx-flask:python3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости Python
COPY requirements.txt /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Копируем файлы приложения в контейнер
COPY main.py /app
COPY settings.py /app
COPY apps /app/apps
COPY static /app/static

# Указываем основной файл приложения (замените app:app на ваше приложение)
ENV MODULE_NAME="app"

