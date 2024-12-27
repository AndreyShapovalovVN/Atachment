from dataclasses import dataclass

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
