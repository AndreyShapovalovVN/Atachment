Для запуска Flask-приложения через Nginx в Windows необходимо немного адаптировать процесс, так как Windows не поддерживает Systemd и некоторые команды Linux. Однако с помощью Nginx и Gunicorn или Waitress можно добиться того же результата.

---

### 1. **Установите Nginx на Windows**

1. Скачайте [Nginx для Windows](https://nginx.org/en/download.html).
2. Распакуйте архив в удобное место, например: `C:\nginx`.
3. Проверьте, что Nginx работает, запустив `nginx.exe`:
   ```cmd
   cd C:\nginx
   start nginx
   ```
   Перейдите в браузере по адресу `http://127.0.0.1`, чтобы убедиться, что Nginx запущен.

---

### 2. **Установите Python и виртуальное окружение**

1. Скачайте и установите [Python для Windows](https://www.python.org/downloads/), убедившись, что вы отметили пункт **Add Python to PATH**.
2. Создайте виртуальное окружение:
   ```cmd
   python -m venv venv
   ```
3. Активируйте виртуальное окружение:
   ```cmd
   venv\Scripts\activate
   ```
   
4. Установите Flask и другие необходимые библиотеки:
   ```cmd
   pip install -r requirements.txt
   ```

---

### 3. **Настройте Gunicorn (или Waitress) для работы с Flask**

Gunicorn не работает в Windows, поэтому вместо него рекомендуется использовать [Waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/).

1. Установите Waitress:
   ```cmd
   pip install waitress
   ```

2. Запустите приложение через Waitress:
   ```cmd
   waitress-serve --host=127.0.0.1 --port=8080 app:app
   ```
   Здесь:
   - `--host=127.0.0.1` — приложение слушает только локальные запросы.
   - `--port=8080` — порт, на котором работает Flask.

---

### 4. **Настройте Nginx**

1. Откройте файл конфигурации `nginx.conf` (обычно находится в `C:\nginx\conf\nginx.conf`).
2. Добавьте новый блок `server` для вашего приложения:

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias C:/path/to/your/app/static;
    }
}
```

3. Перезапустите Nginx:
   ```cmd  nginx.exe -s reload
   ```

---

### 5. **Автоматический запуск приложения и Nginx**

1. **Создайте `.bat`-файл для запуска приложения и Nginx**:
   Создайте файл `start_app.bat` с содержимым:
   ```cmd
   @echo off
   start "" "C:\nginx\nginx.exe"
   cd /d C:\path\to\your\app
   venv\Scripts\activate
   waitress-serve --host=127.0.0.1 --port=8080 app:app
   ```

2. Запустите этот файл вручную или настройте автозапуск через **Task Scheduler**.

---

### 6. **Проверка**

Откройте браузер и перейдите по адресу `http://127.0.0.1`, чтобы проверить, работает ли ваше приложение.

---

### Замечания

- **Nginx на Windows** работает не так стабильно, как на Linux. Если вы разрабатываете на Windows, но деплой планируется на Linux, используйте WSL или Docker.
- **Waitress** — оптимальный WSGI-сервер для Windows, так как Gunicorn не поддерживается.