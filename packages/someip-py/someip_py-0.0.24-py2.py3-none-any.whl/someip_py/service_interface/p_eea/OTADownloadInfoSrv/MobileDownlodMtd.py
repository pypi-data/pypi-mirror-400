from someip_py.codec import *


class IdtMobileDownlodStructureKls(SomeIpPayload):
    _has_dynamic_size = True

    UUID: SomeIpDynamicSizeString

    EcuAddressOTA: SomeIpDynamicSizeString

    DownloadType: SomeIpDynamicSizeString

    EncryptionType: SomeIpDynamicSizeString

    EncryptInfo: SomeIpDynamicSizeString

    SpecifiedurlArray: SomeIpDynamicSizeArray[SomeIpDynamicSizeString]

    URLFlag: SomeIpDynamicSizeString

    def __init__(self):

        self.UUID = SomeIpDynamicSizeString()

        self.EcuAddressOTA = SomeIpDynamicSizeString()

        self.DownloadType = SomeIpDynamicSizeString()

        self.EncryptionType = SomeIpDynamicSizeString()

        self.EncryptInfo = SomeIpDynamicSizeString()

        self.SpecifiedurlArray = SomeIpDynamicSizeArray(SomeIpDynamicSizeString)

        self.URLFlag = SomeIpDynamicSizeString()


class IdtMobileDownlodStructure(SomeIpPayload):

    IdtMobileDownlodStructure: IdtMobileDownlodStructureKls

    def __init__(self):

        self.IdtMobileDownlodStructure = IdtMobileDownlodStructureKls()


class IdtMobileDownlodRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtMobileDownlodRespStruct(SomeIpPayload):

    IdtMobileDownlodRespStruct: IdtMobileDownlodRespStructKls

    def __init__(self):

        self.IdtMobileDownlodRespStruct = IdtMobileDownlodRespStructKls()
