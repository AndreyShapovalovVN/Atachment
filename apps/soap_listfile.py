import logging
import os
from pathlib import Path

from spyne import String, Array, ComplexModel, Unicode
from spyne.model import Fault
from spyne.application import Application
from spyne.decorator import rpc
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase

logger = logging.getLogger(__name__)


class UserDefinedContext(object):
    def __init__(self, flask_config):
        self.config = flask_config


class ListFile(ComplexModel):
    Name = String
    # MD5 = String


class ListOfFiles(ServiceBase):
    __service_name__ = 'ListFiles'

    @rpc(Array(Unicode, min_len=1, nullable=False, patteern='(?!.*\.\.)'), _returns=Array(ListFile))
    def list_files(ctx, dir: list):
        ctx.udc.logger.info(f"Request transaction-id: {ctx.transport.req_env.get('HTTP_UXP_TRANSACTION_ID')}")
        dir = [s for s in dir if ".." not in s and '/' not in s]
        path = Path(ctx.udc.config.get('DOWNLOAD_FOLDER')) / '/'.join(dir)
        if not path.exists():
            ctx.udc.logger.error(f"Path: {path} is not found")
            raise Fault(faultcode="Client.PathNotFound", faultstring=f"File {path} is not found")
        ctx.udc.logger.info(f"Request path: {path}")
        ll = os.listdir(path.as_posix())
        ctx.udc.logger.info(f"List of files: {ll}")
        for file_name in ll:
            yield ListFile(Name=file_name)


def list_files(flask_app):
    application = Application(
        [ListOfFiles],
        name='ListFiles',
        tns='http://Example.org/file/listfile',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )

    # Adding Flask context
    def _flask_config_context(ctx):
        ctx.udc = flask_app

    application.event_manager.add_listener('method_call', _flask_config_context)
    return application
