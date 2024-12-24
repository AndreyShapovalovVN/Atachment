from spyne import ComplexModel, Unicode


# Вложенный объект xro:client
class ClientHeader(ComplexModel):
    __namespace__ = "http://x-road.eu/xsd/identifiers"

    objectType = Unicode.customize(attrname="iden:objectType", type_name="objectType")  # Атрибут в заголовке
    xRoadInstance = Unicode.customize(attrname="iden:xRoadInstance")
    memberClass = Unicode.customize(attrname="iden:memberClass")
    memberCode = Unicode.customize(attrname="iden:memberCode")
    subsystemCode = Unicode.customize(attrname="iden:subsystemCode", min_occurs=0)  # Optional


# Вложенный объект xro:service
class ServiceHeader(ClientHeader):
    serviceCode = Unicode.customize(attrname="iden:serviceCode")  # Optional


# Общий объект для заголовка
class XRoadHeader(ComplexModel):
    __namespace__ = "http://x-road.eu/xsd/xroad.xsd"

    client = ClientHeader.customize(min_occurs=1)
    service = ServiceHeader.customize(min_occurs=1)
    userId = Unicode.customize(attrname="xro:userId", type_name="userId")
    id = Unicode.customize(attrname="xro:id", type_name="id")
    protocolVersion = Unicode.customize(attrname="xro:protocolVersion", type_name="protocolVersion")
