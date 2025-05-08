import logging

from flask import Flask, request
from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from apps.soap_MTOM import getMTOM
from apps.soap_listfile import list_files

app = Flask(__name__)
app.config.from_object('settings.Config')
app.logger.setLevel(logging.DEBUG)


@app.before_request
def log_request_info():
    app.logger.info(f"Incoming request: {request.method} {request.url}")


@app.after_request
def log_response_info(response):
    app.logger.info(f"Response status: {response.status}")
    return response


@app.route('/')
def hello():  # put application's code here
    return """Цей Веб-сервіс був створений у рамках експертной допомоги 
Державній Казначейскій служби України експертом з інтерперабільності та 
розвитку реєстрів Академії електроного управління Республіки Естонія у 2024 році 
Андрієм Шаповаловим

Ісходний код буде доступний на GitHub після завершення проекту

e-mail: andrei.shapovalov@ega.ee"""


app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app,
    {'/listfiles': WsgiApplication(list_files(app)),
     '/download': WsgiApplication(getMTOM(app))}
)

if __name__ == '__main__':
    app.run()
