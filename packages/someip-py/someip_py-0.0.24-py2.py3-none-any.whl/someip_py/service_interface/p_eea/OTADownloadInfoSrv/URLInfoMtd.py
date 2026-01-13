from someip_py.codec import *


class IdtOTAURLInfoStructKls(SomeIpPayload):
    _has_dynamic_size = True

    InstallationorderUUID: SomeIpDynamicSizeString

    EcuAddressOTA: SomeIpDynamicSizeString

    DownloadType: SomeIpDynamicSizeString

    EncryptionType: SomeIpDynamicSizeString

    EncryptInfo: SomeIpDynamicSizeString

    SpecifiedurlArray: SomeIpDynamicSizeArray[SomeIpDynamicSizeString]

    FileSize: Uint32

    def __init__(self):

        self.InstallationorderUUID = SomeIpDynamicSizeString()

        self.EcuAddressOTA = SomeIpDynamicSizeString()

        self.DownloadType = SomeIpDynamicSizeString()

        self.EncryptionType = SomeIpDynamicSizeString()

        self.EncryptInfo = SomeIpDynamicSizeString()

        self.SpecifiedurlArray = SomeIpDynamicSizeArray(SomeIpDynamicSizeString)

        self.FileSize = Uint32()


class IdtOTAURLInfoStruct(SomeIpPayload):

    IdtOTAURLInfoStruct: IdtOTAURLInfoStructKls

    def __init__(self):

        self.IdtOTAURLInfoStruct = IdtOTAURLInfoStructKls()


class IdtOTAURLInfoRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtOTAURLInfoRespStruct(SomeIpPayload):

    IdtOTAURLInfoRespStruct: IdtOTAURLInfoRespStructKls

    def __init__(self):

        self.IdtOTAURLInfoRespStruct = IdtOTAURLInfoRespStructKls()
