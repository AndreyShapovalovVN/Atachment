import uuid
from os import path

from flask import Response
from lxml import etree

from apps.ParseRequestForMTOM import ParseXMLRequest
from apps.read_file import read_file


def response(app, request):
    dict_request = ParseXMLRequest(app, request)
    path_to_file = path.join('.',
                             app.config.get('DOWNLOAD_FOLDER'),
                             dict_request.clent.memberCode,
                             dict_request.params.account,
                             dict_request.params.file_name)
    if not path.isfile(path_to_file):
        app.logger.error(f'File {path_to_file} not found')
        error = FileNotFoundError()
        error.xml(f'File {path_to_file} not found')
        return error.message
    file = read_file(path_to_file)
    app.logger.info(f'Sending file: {file.get("file_name")} '
                    f'MD5: {file.get("file_md5")} '
                    f'to client: {dict_request.clent.client_id}')
    mtom = MTOM(status=200)
    mtom.file = file
    mtom.request = dict_request
    return mtom.message


class Message:
    def __init__(self, status: int = None, headers: dict = dict(), data: bytes = b'None'):
        self.response = Response()
        self.response.status = status
        self.response.headers.update(headers)
        self.data = data
        # self.response.data = data

    @property
    def message(self):
        return self.response


class MTOM(Message):
    def __init__(self, status: int = None, headers: dict = dict(), data: bytes = b'None'):
        super().__init__(status, headers, data)
        self.request: dict = dict()
        self.file: dict = dict()

        self.cid0 = f'0.urn:uuid:{uuid.uuid4().hex}@dksu.gov.ua'
        self.cid1 = f'1.urn:uuid:{uuid.uuid4().hex}@dksu.gov.ua'
        self.MIMEBoundary = uuid.uuid4().hex

    @property
    def xml(self):
        ns = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
              'mtom': 'http://dksu.gov.ua/mtom',
              'xop': "http://www.w3.org/2004/08/xop/include"}
        envelope = etree.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope', nsmap=ns)
        header = etree.SubElement(envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Header')
        body = etree.SubElement(envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        AttachmentRequest = etree.SubElement(body, '{http://dksu.gov.ua/mtom}AttachmentRequest', nsmap=ns)
        FileMetadata = etree.SubElement(AttachmentRequest, '{http://dksu.gov.ua/mtom}FileMetadata')
        etree.SubElement(FileMetadata, '{http://dksu.gov.ua/mtom}FileName').text = self.request.params.file_name
        etree.SubElement(FileMetadata, '{http://dksu.gov.ua/mtom}FileType').text = self.file.get('file_mime')
        etree.SubElement(FileMetadata, '{http://dksu.gov.ua/mtom}FileMD5').text = self.file.get('file_md5')

        FileContent = etree.SubElement(AttachmentRequest, '{http://dksu.gov.ua/mtom}FileContent')
        Include = etree.SubElement(FileContent, '{http://www.w3.org/2004/08/xop/include}Include')
        Include.attrib['href'] = f'cid:{self.cid1}'

        return etree.tostring(envelope, pretty_print=True, xml_declaration=True, encoding='utf-8')

    def _data(self):
        mime = list()
        mime.append(f'--MIMEBoundary{self.MIMEBoundary}'.encode('utf-8'))
        mime.append('Content-Type: application/xop+xml; charset=UTF-8; type="text/xml";'.encode('utf-8'))
        mime.append('Content-Transfer-Encoding: binary'.encode('utf-8'))
        mime.append(f'Content-ID: <{self.cid0}>'.encode('utf-8'))
        mime.append(b'')
        mime.append(self.xml)
        mime.append(f'--MIMEBoundary{self.MIMEBoundary}'.encode('utf-8'))
        mime.append(f'Content-Type: {self.file.get("file_mime")}'.encode('utf-8'))
        mime.append(b'Content-Transfer-Encoding: binary')
        mime.append(f'Content-Id: <{self.cid1}>'.encode('utf-8'))
        mime.append(f'Content-Disposition: attachment; '
                    f'name="{self.file.get("file_name")}"; '
                    f'filename="{self.file.get("file_name")}"'.encode('utf-8'))
        mime.append(b'')
        mime.append(self.file['file_data'])
        mime.append(f'--MIMEBoundary{self.MIMEBoundary}--'.encode('utf-8'))
        self.response.data = b'\n'.join(mime)

    def _headers(self):
        self.response.headers.update({'Content-Type': (f'multipart/related; '
                                                       f'boundary="MIMEBoundary{self.MIMEBoundary}"; '
                                                       f'type="application/xop+xml"; '
                                                       f'start="<{self.cid0}>"; '
                                                       f'start-info="text/xml"; '
                                                       f'charset=UTF-8')})

    @property
    def message(self):
        self._headers()
        self._data()
        return self.response


class FileNotFoundError(Message):
    def __init__(self):
        super().__init__(404, {'Content-Type': 'text/xml'}, None)

    def xml(self, text):
        ns = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/'}
        envelope = etree.Element('{http://schemas.xmlsoap.org/soap/envelope/}Envelope', nsmap=ns)
        body = etree.SubElement(envelope, '{http://schemas.xmlsoap.org/soap/envelope/}Body')
        fault = etree.SubElement(body, '{http://schemas.xmlsoap.org/soap/envelope/}Fault')
        etree.SubElement(fault, '{http://schemas.xmlsoap.org/soap/envelope/}faultcode').text = f'soapenv:Client'
        etree.SubElement(fault, '{http://schemas.xmlsoap.org/soap/envelope/}faultstring').text = f'File not found'
        etree.SubElement(fault, '{http://schemas.xmlsoap.org/soap/envelope/}detail').text = text

        self.response.data = etree.tostring(envelope, pretty_print=True, xml_declaration=True, encoding='utf-8')

        return self
