from os import path

from spyne import Fault
from spyne import ServiceBase
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.primitive import Mandatory
from spyne.protocol.soap import Soap11

from apps.model.MTOM import FileMetadata, FileContent, MTOMAttachment
from apps.protocol.MTOM import MTOM
from apps.tools.TrembitaHeader import Client
from apps.tools.read_file import read_file


class mtom(ServiceBase):
    @rpc(Mandatory.String, Mandatory.Date, Mandatory.Integer, Mandatory.String, _returns=MTOMAttachment)
    def get(ctx, account, date, parttition, tag):
        ctx.udc.logger.info(f"Request transaction-id: {ctx.transport.req_env.get('HTTP_UXP_TRANSACTION_ID')}")
        client = Client(ctx.in_document, 'client')
        if not client:
            ctx.udc.logger.error("No headers received")
            raise Fault(faultcode="Client.NoHeaders", faultstring="No headers received")
        ctx.udc.logger.info(f"Request client: {client.client_id}")

        if not isinstance(date, str):
            date = date.strftime('%Y%m%d')

        filename = f'{date}_{str(parttition).zfill(2)}_{tag}.zip'
        path_to_file = path.join('.',
                                 ctx.udc.config.get('DOWNLOAD_FOLDER'),
                                 client.dict().get('memberCode'),
                                 account,
                                 filename)
        if not path.isfile(path_to_file):
            ctx.udc.logger.error(f'File {path_to_file} not found')
            raise Fault(faultcode="Client.FileNotFound", faultstring=f"File {path_to_file} not found")
        file = read_file(path_to_file)

        ctx.out_protocol.FileName = filename
        ctx.out_protocol.FileType = file.get('file_mime')
        ctx.out_protocol.FileData = file.get('file_data')

        ctx.udc.logger.info(f'Sending file: {file.get("file_name")} '
                            f'MD5: {file.get("file_md5")} '
                            f'to client: {client.client_id}')
        ar = MTOMAttachment(
            FileMetadata=FileMetadata(
                FileName=ctx.out_protocol.FileName,
                FileType=ctx.out_protocol.FileType,
                FileMD5=file.get('file_md5')
            ),
            FileContent=FileContent(
                Include={"href": f'cid:{ctx.out_protocol.cid1}'}
            )
        )
        return ar


def getMTOM(flask_app):
    application = Application(
        [mtom],
        tns='http://dksu.gov.ua/file/download',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=MTOM()
    )

    # Adding Flask context
    def _flask_config_context(ctx):
        ctx.udc = flask_app

    application.event_manager.add_listener('method_call', _flask_config_context)
    return application
