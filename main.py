import logging
import os

from flask import Flask, send_file, request
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


@app.route('/download/<account>/<date>/<parttition>/<tag>')
def download(account, date, parttition, tag):
    file_name = f'{date}_{parttition}_{tag}.zip'
    app.logger.info(f"Request transaction-id: {request.headers.get('uxp-transaction-id')}")
    app.logger.info(f"Request client: {request.headers.get('Uxp-Client')}")
    app.logger.info(f"Request parametrs: {account} {date} {parttition} {tag}")
    app.logger.info(f"Request file: {file_name}")
    return send_file(os.path.join(app.config.get('DOWNLOAD_FOLDER'), account, file_name), as_attachment=True)


app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app,
    {'/listfiles': WsgiApplication(list_files(app)),
     '/mtom': WsgiApplication(getMTOM(app))}
)

if __name__ == '__main__':
    app.run()
