import logging
import os

from flask import Flask, send_file, request
from spyne.server.wsgi import WsgiApplication
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from apps.createMessageMTOM import response
from apps.soap_get_file import list_files, get_file

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


@app.route('/mtom')
def soap():
    if 'wsdl' in request.args.keys() and request.method == 'GET':
        return send_file(os.path.join(app.config.get('DOWNLOAD_WSDL'), 'mtom.wsdl'), as_attachment=True)
    return response(app, request)


app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app,
    {'/soap': WsgiApplication(get_file(app)), }
)

app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app,
    {'/listfiles': WsgiApplication(list_files(app))}
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
