import uuid

from lxml import etree
from spyne.protocol.soap import Soap11


class MTOM(Soap11):

    def __init__(self, app=None):
        super().__init__(app, validator=None)
        self.FileData = b''
        self.FileName = ''
        self.FileType = ''
        self.cid0 = uuid.uuid4().hex
        self.MIMEBoundary = uuid.uuid4().hex

    @property
    def cid1(self):
        return self.FileName

    def serialize(self, ctx, message):
        super().serialize(ctx, message)
        ctx.transport.resp_headers.update(
            {'Content-Type': (f'multipart/related; '
                              f'boundary="MIMEBoundary{self.MIMEBoundary}"; '
                              f'type="application/xop+xml"; '
                              f'start="<{self.cid0}>"; '
                              f'start-info="text/xml"; '
                              f'charset=UTF-8')}
        )

    def create_out_string(self, ctx, out_string_encoding=None):
        ctx.out_string = []
        ctx.out_string.append(f'--MIMEBoundary{self.MIMEBoundary}\n'.encode('utf-8'))
        ctx.out_string.append('Content-Type: application/xop+xml; charset=UTF-8; type="text/xml";\n'.encode('utf-8'))
        ctx.out_string.append('Content-Transfer-Encoding: binary\n'.encode('utf-8'))
        ctx.out_string.append(f'Content-ID: <{self.cid0}>\n'.encode('utf-8'))
        ctx.out_string.append('\n'.encode('utf-8'))

        ctx.out_string.append(
            etree.tostring(ctx.out_document, pretty_print=True, encoding='utf8', xml_declaration=True))

        ctx.out_string.append(f'--MIMEBoundary{self.MIMEBoundary}\n'.encode('utf-8'))
        ctx.out_string.append(f'Content-Type: {self.FileType}\n'.encode('utf-8'))
        ctx.out_string.append(b'Content-Transfer-Encoding: binary\n')
        ctx.out_string.append(f'Content-Id: <{self.cid1}>\n'.encode('utf-8'))
        ctx.out_string.append(f'Content-Disposition: attachment; '
                              f'name="{self.FileName}"; '
                              f'filename="{self.FileName}"\n'.encode('utf-8'))
        ctx.out_string.append('\n'.encode('utf-8'))
        ctx.out_string.append(self.FileData)
        ctx.out_string.append('\n'.encode('utf-8'))
        ctx.out_string.append(f'--MIMEBoundary{self.MIMEBoundary}--'.encode('utf-8'))

    def decompose_incoming_envelope(self, ctx, message):
        raise NotImplementedError("This is an output-only protocol.")
