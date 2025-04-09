import logging
import os

from spyne import String, Array, Fault, ComplexModel
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.primitive import Mandatory
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase

from apps.tools.TrembitaHeader import Client

logger = logging.getLogger(__name__)


class UserDefinedContext(object):
    def __init__(self, flask_config):
        self.config = flask_config


class ListFile(ComplexModel):

    Name = String
    # MD5 = String


class ListOfFiles(ServiceBase):
    __service_name__ = 'ListFiles'
    @rpc(Mandatory.String(patteern='^UA\d+$'), _returns=Array(ListFile))
    def list_files(ctx, account):
        ctx.udc.logger.info(f"Request transaction-id: {ctx.transport.req_env.get('HTTP_UXP_TRANSACTION_ID')}")
        client = Client(ctx.in_document, 'client')
        if not client:
            ctx.udc.logger.error("No headers received")
            raise Fault(faultcode="Client.NoHeaders", faultstring="No headers received")
        ctx.udc.logger.info(f"Request client: {client.client_id}")
        ctx.udc.logger.info(f"Request account: {account}")
        ll = os.listdir(os.path.join(ctx.udc.config.get('DOWNLOAD_FOLDER'), client.dict().get('memberCode'), account))
        ctx.udc.logger.info(f"List of files: {ll}")
        for file_name in ll:
            yield ListFile(Name=file_name)


def list_files(flask_app):
    application = Application(
        [ListOfFiles],
        name='ListFiles',
        tns='http://dksu.gov.ua/file/listfile',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )

    # Adding Flask context
    def _flask_config_context(ctx):
        ctx.udc = flask_app

    application.event_manager.add_listener('method_call', _flask_config_context)
    return application
