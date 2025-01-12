import logging

logger = logging.getLogger('spyne.protocol.MTOM')
logger_invalid = logging.getLogger('spyne.protocol.MTOM.invalid')

import uuid

from lxml import etree
from spyne.protocol.soap import Soap11
from apps.model.MTOM import MTOMAttachment


class MTOM(Soap11):
    """
    MTOM protocol implementation.
    """

    def __init__(self, app=None):
        super().__init__(app, validator=None)
        self.FileData = b''
        self.FileName = ''
        self.FileType = ''
        self.cid0 = uuid.uuid4().hex
        self.MIMEBoundary = uuid.uuid4().hex
        self.base64 = base64

    @property
    def cid1(self):
        return self.FileName

    def serialize(self, ctx, message):
        """
        Serialize the message to the output stream.
        :param ctx:
        :param message:
        :return:
        """
        super().serialize(ctx, message)
        if not ctx.out_object:
            logger_invalid.error("No out_object found.")
            return
        if not isinstance(ctx.out_object[0], MTOMAttachment):
            logger_invalid.error("No MTOMAttachment found.")
            return

        logger.debug("Creating MTOM envelop.")
        self.FileName = ctx.out_object[0].FileMetadata.FileName
        self.FileType = ctx.out_object[0].FileMetadata.FileType
        self.FileData = ctx.out_object[0].FileContent.FileData

        logger.debug("Creating MTOM headers.")
        ctx.transport.resp_headers.update(
            {'Content-Type': (f'multipart/related; '
                              f'boundary="MIMEBoundary{self.MIMEBoundary}"; '
                              f'type="application/xop+xml"; '
                              f'start="<{self.cid0}>"; '
                              f'start-info="text/xml"; '
                              f'charset=UTF-8')}
        )
        logger.debug("MTOM Content-Type: %s", ctx.transport.resp_headers['Content-Type'])

        logger.debug("Remove element FileData for out_body_doc.")
        FileContent = ctx.out_body_doc.xpath(f'//*[local-name() = "FileContent"]')[0]
        FileContent.remove(FileContent.xpath(f'//*[local-name() = "FileData"]')[0])

        logger.info('MTOM response serialize.')

    def create_xml_out_section(self, ctx):
        """
        Create the XML section of the MTOM message.
        :param ctx:
        :return:
        """
        logger.debug("Creating MTOM XML section.")
        ctx.out_string.append(f'--MIMEBoundary{self.MIMEBoundary}\r\n'.encode('utf-8'))
        ctx.out_string.append('Content-Type: application/xop+xml; charset=UTF-8; type="text/xml";\r\n'.encode('utf-8'))
        ctx.out_string.append('Content-Transfer-Encoding: binary\r\n'.encode('utf-8'))
        ctx.out_string.append(f'Content-ID: <{self.cid0}>\r\n'.encode('utf-8'))
        ctx.out_string.append('\r\n'.encode('utf-8'))
        ctx.out_string.append(
            etree.tostring(ctx.out_document, pretty_print=True, encoding='utf8', xml_declaration=True))
        ctx.out_string.append('\r\n'.encode('utf-8'))

    def create_data_out_section_bin(self, ctx):
        """
        Create the data section of the MTOM message.
        :param ctx:
        :return:
        """
        ctx.out_string.append(f'--MIMEBoundary{self.MIMEBoundary}\r\n'.encode('utf-8'))
        ctx.out_string.append(f'Content-Type: {self.FileType}; name={self.FileName}\r\n'.encode('utf-8'))
        ctx.out_string.append(b'Content-Transfer-Encoding: binary\r\n')

        ctx.out_string.append(f'Content-Id: <{self.cid1}>\r\n'.encode('utf-8'))
        ctx.out_string.append(f'Content-Disposition: attachment; '
                              f'name="{self.FileName}"; '
                              f'filename="{self.FileName}"\r\n'.encode('utf-8'))
        ctx.out_string.append('\r\n'.encode('utf-8'))
        ctx.out_string.append(self.FileData)
        ctx.out_string.append('\r\n'.encode('utf-8'))
        ctx.out_string.append(f'--MIMEBoundary{self.MIMEBoundary}--\r\n'.encode('utf-8'))

    def create_out_string(self, ctx, out_string_encoding=None):
        """
        Create the MTOM message.
        :param ctx:
        :param out_string_encoding:
        :return:
        """
        super().create_out_string(ctx, out_string_encoding)
        if not ctx.out_object:
            return

        if not isinstance(ctx.out_object[0], MTOMAttachment):
            return

        logger.debug("Creating MTOM message.")
        ctx.out_string = []

        logger.debug("Creating MTOM XML section.")
        self.create_xml_out_section(ctx)

        logger.debug("Creating MTOM data section.")
        self.create_data_out_section_bin(ctx)

        logger.debug("MTOM body created.")
        logger.debug("MTOM message length: %s", len(ctx.out_string))
        logger.debug("MTOM message: %s", ctx.out_string)

    def decompose_incoming_envelope(self, ctx, message):
        """
        Decompose the incoming message.
        :param ctx:
        :param message:
        :return:
        """
        logger_invalid.error("This is an output-only protocol.")
        raise NotImplementedError("This is an output-only protocol.")
