from dataclasses import dataclass
from datetime import datetime
from os import path
from lxml import etree


@dataclass
class XMLXpach:
    elements: etree.Element
    search_key: str

    def __post_init__(self):
        for i, element in enumerate(self.elements.xpath(f"//*[local-name() = '{self.search_key}']")[0].iter()):
            if not isinstance(element.tag, str):
                continue
            if i == 0:
                continue
            setattr(self, etree.QName(element.tag).localname, element.text)

    def dict(self):
        return {k: v for k, v in self.__dict__.items() if k not in ['elements', 'search_key']}


class Client(XMLXpach):
    search_key = 'client'

    @property
    def client_id(self):
        return f"{self.xRoadInstance}/{self.memberClass}/{self.memberCode}/{self.subsystemCode}"


class Param(XMLXpach):

    @property
    def file_name(self):
        if isinstance(self.date, datetime):
            date = datetime.strftime(self.date, '%Y%m%d')
        elif isinstance(self.date, str):
            date = self.date.replace('-', '')
        else:
            raise ValueError('Date must be string or datetime.date')
        return f'{date}_{str(self.parttition).zfill(2)}_{self.tag}.zip'


class ParseXMLRequest:
    def __init__(self, app, request):
        self.app = app
        self.request = request
        self.xml = etree.fromstring(request.data.decode('utf-8'))

        self.uxp_transaction_id: str = self.request.headers.get('uxp-transaction-id')
        self.clent: dataclass = Client(self.xml, 'client')
        self.id: str | None = None
        self.params: dataclass = Param(self.xml, 'get')
        self._logging()

    def _logging(self):
        self.app.logger.info(f"Request transaction-id: {self.request.headers.get('uxp-transaction-id')}")
        self.app.logger.info(f"Request client: {self.clent.client_id}")
        self.app.logger.info(f"Request parametrs: {self.params.dict()}")
