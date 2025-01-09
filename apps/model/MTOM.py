"""
Модель для обміну файлами з використанням MTOM
"""
import logging

logger = logging.getLogger('spyne.model.MTOM')
logger_invalid = logging.getLogger('spyne.model.MTOM.invalid')

import tempfile
import pathlib
import hashlib

import magic
from spyne import XmlAttribute
from spyne.model.binary import ByteArray
from spyne.model.complex import ComplexModel
from spyne.model.primitive import Mandatory, Unicode


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
    FileData = ByteArray(logged='len')


class MTOMAttachment(ComplexModel):
    # Вкладені елементи
    FileMetadata = FileMetadata.customize(attrname="mtom:FileMetadata")
    FileContent = FileContent.customize(attrname="mtom:FileContent")

    def __init__(self, path=None, name=None, data=None):
        mime = None
        if path is not None:
            if pathlib.Path(path).exists():
                name = pathlib.Path(path).name
                data = open(path, 'rb').read()
                mime = magic.Magic(mime=True).from_file(path)
        if mime is None:
            file = tempfile.NamedTemporaryFile(delete=False)
            file.write(data)
            file.close()
            pach = pathlib.Path(file.name)
            mime = magic.Magic(mime=True).from_file(pach)
            name = pach.name

        self.FileContent = FileContent(Inclode=URI.customize(attrname="xor:Include"),
                                       FileData=ByteArray(logged='len'))
        self.FileContent.Include = {"href": f'cid:{name}'}
        self.FileContent.FileData = data

        self.FileMetadata = FileMetadata(FileName=name,
                                         FileType=mime,
                                         FileMD5=hashlib.md5(self.FileContent.FileData).hexdigest())
