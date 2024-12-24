import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

from spyne import String, Array, Fault, ComplexModel, File
from spyne.application import Application
from spyne.decorator import rpc
from spyne.service import ServiceBase
from spyne.model.primitive import Mandatory
from spyne.protocol.soap import Soap11

from apps.XRoadHeader import XRoadHeader
from apps.ParseRequestForMTOM import Client
from apps.read_file import read_file


class UserDefinedContext(object):
    def __init__(self, flask_config):
        self.config = flask_config


class ListFile(ComplexModel):
    Name = String
    # MD5 = String


class ListOfFiles(ServiceBase):
    __in_header__ = XRoadHeader

    @rpc(Mandatory.String, _returns=Array(ListFile))
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
        tns='spyne.examples.flask',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )

    # Adding Flask context
    def _flask_config_context(ctx):
        ctx.udc = flask_app

    application.event_manager.add_listener('method_call', _flask_config_context)
    return application


#
class FileServices(ServiceBase):
    @rpc(Mandatory.String, Mandatory.Date, Mandatory.Integer, Mandatory.String, _returns=File)
    def get(ctx, account, date, parttition, tag):
        ctx.udc.logger.info(f"Request transaction-id: {ctx.transport.req_env.get('HTTP_UXP_TRANSACTION_ID')}")
        client = Client(ctx.in_document, 'client')
        if not client:
            ctx.udc.logger.error("No headers received")
            raise Fault(faultcode="Client.NoHeaders", faultstring="No headers received")
        ctx.udc.logger.info(f"Request client: {client.client_id}")
        ctx.udc.logger.info(f"Request account: {account}")

        fname = f'{datetime.strftime(date, '%Y%m%d')}_{str(parttition).zfill(2)}_{tag}.zip'
        file = read_file(os.path.join(ctx.udc.config.get('DOWNLOAD_FOLDER'),
                                      client.dict().get('memberCode'),
                                      account,
                                      fname)
                         )
        ctx.udc.logger.info(f'Sending file: {file.get("file_name")} ')
        return File.Value(data=file.get('file_data'), name=fname, )


def get_file(flask_app):
    application = Application(
        [FileServices], tns='spyne.examples.flask',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )

    def _flask_config_context(ctx):
        ctx.udc = flask_app

    application.event_manager.add_listener('method_call', _flask_config_context)
    return application
