from pathlib import Path

from spyne import ServiceBase, Array, Unicode
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model import Fault
from spyne.model.primitive import Mandatory
from spyne.protocol.soap import Soap11

from apps.model.MTOM import MTOMAttachment
from apps.protocol.MTOM import MTOM


class Mtom(ServiceBase):
    __service_name__ = 'Download'

    @rpc(Array(Unicode, min_len=1, nullable=False, patteern='(?!.*\.\.)'),
         Mandatory.String(),
         _returns=MTOMAttachment)
    def mtom(ctx, dir: list, filename: str):
        ctx.udc.logger.info(f"Request transaction-id: {ctx.transport.req_env.get('HTTP_UXP_TRANSACTION_ID')}")
        dir = [s for s in dir if ".." not in s]
        path_to_file = Path(ctx.udc.config.get('DOWNLOAD_FOLDER')) / '/'.join(dir) / filename

        if not path_to_file.exists():
            ctx.udc.logger.error(f"File: {path_to_file} is not found")
            raise Fault(faultcode="Client.FileNotFound", faultstring=f"File {path_to_file.name} is not found")
        ctx.udc.logger.info(f"File: {path_to_file} is sending")
        return MTOMAttachment(path=path_to_file)


def getMTOM(flask_app):
    application = Application(
        [Mtom],
        name='Download',
        tns='http://Example.org/file/download',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=MTOM()
    )

    # Adding Flask context
    def _flask_config_context(ctx):
        ctx.udc = flask_app

    application.event_manager.add_listener('method_call', _flask_config_context)
    return application
