"""
Модель для обміну файлами з використанням MTOM
"""

from spyne.model.complex import ComplexModel
from spyne.model.primitive import Mandatory, Unicode
from spyne import XmlAttribute


class FileMetadata(ComplexModel):
    # Елементи метаданих файлу
    FileName = Mandatory.String(attrname="mtom:FileName")
    FileType = Mandatory.String(attrname="mtom:FileType")
    FileMD5 = Unicode.customize(attrname="mtom:FileMD5")


class URI(Mandatory.AnyXml):
    href = XmlAttribute(Mandatory.String)


class FileContent(ComplexModel):
    __namespace__ = "http://www.w3.org/2004/08/xop/include/"
    # Елемент <xop:Include> з атрибутом href
    Include = URI.customize(attrname="xor:Include")


class MTOMAttachment(ComplexModel):
    # Вкладені елементи
    FileMetadata = FileMetadata.customize(attrname="mtom:FileMetadata")
    FileContent = FileContent.customize(attrname="mtom:FileContent")
