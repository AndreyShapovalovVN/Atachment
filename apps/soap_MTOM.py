from pathlib import Path

from spyne import ServiceBase
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model import Fault
from spyne.model.primitive import Mandatory
from spyne.protocol.soap import Soap11

from apps.model.MTOM import MTOMAttachment
from apps.protocol.MTOM import MTOM
from apps.tools.TrembitaHeader import Client, ClientTest


class Mtom(ServiceBase):
    @rpc(Mandatory.String, Mandatory.Date, Mandatory.Integer, Mandatory.String,
         _returns=MTOMAttachment)
    def mtom(ctx, account, date, parttition, tag):
        ctx.udc.logger.info(f"Request transaction-id: {ctx.transport.req_env.get('HTTP_UXP_TRANSACTION_ID')}")
        try:
            client = Client(ctx.in_document, 'client')
        except Exception as e:
            ctx.udc.logger.error(f"Error: {e}")
            client = ClientTest(ctx.in_document, 'client')
            # raise Fault(faultcode="Client.NoHeaders", faultstring="No headers received")

        ctx.udc.logger.info(f"Request client: {client.client_id}")

        if not isinstance(date, str):
            date = date.strftime('%Y%m%d')

        filename = f'{date}_{str(parttition).zfill(2)}_{tag}.zip'
        path_to_file = Path(ctx.udc.config.get('DOWNLOAD_FOLDER')) / client.memberCode / account / filename
        if not path_to_file.exists():
            ctx.udc.logger.error(f"File: {path_to_file} is not found")
            raise Fault(faultcode="Client.FileNotFound", faultstring=f"File {path_to_file.name} is not found")
        ctx.udc.logger.info(f"File: {path_to_file} is sending")
        return MTOMAttachment(path=path_to_file)


def getMTOM(flask_app):
    application = Application(
        [Mtom],
        tns='http://dksu.gov.ua/file/download',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=MTOM()
    )

    # Adding Flask context
    def _flask_config_context(ctx):
        ctx.udc = flask_app

    application.event_manager.add_listener('method_call', _flask_config_context)
    return application
