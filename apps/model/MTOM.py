"""
Модель для обміну файлами з використанням MTOM
"""
import logging

logger = logging.getLogger('spyne.model.MTOM')
logger_invalid = logging.getLogger('spyne.model.MTOM.invalid')

import tempfile
from pathlib import Path
import hashlib

import magic
from spyne import XmlAttribute
from spyne.model.binary import ByteArray
from spyne.model.complex import ComplexModel
from spyne.model.primitive import Mandatory, Unicode


class FileMetadata(ComplexModel):
    """
    Метадані файлу
    """
    # Елементи метаданих файлу
    FileName = Mandatory.String(attrname="mtom:FileName")
    FileType = Mandatory.String(attrname="mtom:FileType")
    FileMD5 = Unicode.customize(attrname="mtom:FileMD5")


class URI(Mandatory.AnyXml):
    """
    Клас для обробки атрибутів типу URI
    """
    href = XmlAttribute(Mandatory.String)


class FileContent(ComplexModel):
    """
    Вміст файлу
    """
    __namespace__ = "http://www.w3.org/2004/08/xop/include/"
    # Елемент <xop:Include> з атрибутом href
    Include = URI.customize(attrname="xor:Include")
    FileData = ByteArray(logged='len')


class MTOMAttachment(ComplexModel):
    """
    Клас для обміну файлами з використанням MTOM
    """
    FileMetadata = FileMetadata.customize(attrname="mtom:FileMetadata")
    FileContent = FileContent.customize(attrname="mtom:FileContent")

    def __init__(self,
                 path: str | None = None,
                 name: str | None = None,
                 data: bytes | None = None) -> None:
        """
        Конструктор класу
        :param path:
        :param name:
        :param data:
        """
        mime = None
        path = Path(path)
        if path is not None:
            if path.exists():
                name = path.name
                data = open(path, 'rb').read()
                mime = magic.Magic(mime=True).from_file(path.as_posix())
        if mime is None and data is not None:
            file = tempfile.NamedTemporaryFile(delete=True)
            file.write(data)
            file.close()
            pach = Path(file.name)
            mime = magic.Magic(mime=True).from_file(pach.as_posix())
            name = pach.name

        self.FileContent = FileContent(Inclode=URI.customize(attrname="xor:Include"),
                                       FileData=ByteArray(logged='len'))
        self.FileContent.Include = {"href": f'cid:{name}'}
        self.FileContent.FileData = data

        self.FileMetadata = FileMetadata(FileName=name,
                                         FileType=mime,
                                         FileMD5=hashlib.md5(self.FileContent.FileData).hexdigest())
