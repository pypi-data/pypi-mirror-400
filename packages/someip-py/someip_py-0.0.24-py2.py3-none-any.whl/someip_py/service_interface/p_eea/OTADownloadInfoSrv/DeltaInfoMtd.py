from someip_py.codec import *


class IdtSoftwarePartDeltaInfoStruct(SomeIpPayload):

    FileName: SomeIpDynamicSizeString

    PartType: SomeIpDynamicSizeString

    OTaFileSize: Uint32

    IsDelta: Uint8

    Reserve1: SomeIpDynamicSizeString

    def __init__(self):

        self.FileName = SomeIpDynamicSizeString()

        self.PartType = SomeIpDynamicSizeString()

        self.OTaFileSize = Uint32()

        self.IsDelta = Uint8()

        self.Reserve1 = SomeIpDynamicSizeString()


class IdtDeltaUrl(SomeIpPayload):
    _has_dynamic_size = True

    EcuAddress: SomeIpDynamicSizeString

    DownloadType: SomeIpDynamicSizeString

    FileEncryptionType: SomeIpDynamicSizeString

    EncryptInfo: SomeIpDynamicSizeString

    DeltaUrlList: SomeIpDynamicSizeArray[SomeIpDynamicSizeString]

    FileSize: Uint32

    Reserve1: SomeIpDynamicSizeString

    def __init__(self):

        self.EcuAddress = SomeIpDynamicSizeString()

        self.DownloadType = SomeIpDynamicSizeString()

        self.FileEncryptionType = SomeIpDynamicSizeString()

        self.EncryptInfo = SomeIpDynamicSizeString()

        self.DeltaUrlList = SomeIpDynamicSizeArray(SomeIpDynamicSizeString)

        self.FileSize = Uint32()

        self.Reserve1 = SomeIpDynamicSizeString()


class IdtOTADeltaInfoStructKls(SomeIpPayload):
    _has_dynamic_size = True

    UUID: SomeIpDynamicSizeString

    Ecuaddress: SomeIpDynamicSizeString

    EnableDelta: Uint8

    DownloadStrategy: Uint32

    InstallationStrategy: Uint32

    SoftwarePartDeltaInfoArray: SomeIpDynamicSizeArray[IdtSoftwarePartDeltaInfoStruct]

    DeltaUrls: IdtDeltaUrl

    Reserve1: SomeIpDynamicSizeString

    Reserve2: SomeIpDynamicSizeString

    def __init__(self):

        self.UUID = SomeIpDynamicSizeString()

        self.Ecuaddress = SomeIpDynamicSizeString()

        self.EnableDelta = Uint8()

        self.DownloadStrategy = Uint32()

        self.InstallationStrategy = Uint32()

        self.SoftwarePartDeltaInfoArray = SomeIpDynamicSizeArray(
            IdtSoftwarePartDeltaInfoStruct
        )

        self.DeltaUrls = IdtDeltaUrl()

        self.Reserve1 = SomeIpDynamicSizeString()

        self.Reserve2 = SomeIpDynamicSizeString()


class IdtOTADeltaInfoStruct(SomeIpPayload):

    IdtOTADeltaInfoStruct: IdtOTADeltaInfoStructKls

    def __init__(self):

        self.IdtOTADeltaInfoStruct = IdtOTADeltaInfoStructKls()


class IdtOTADeltaInfoRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtOTADeltaInfoRespStruct(SomeIpPayload):

    IdtOTADeltaInfoRespStruct: IdtOTADeltaInfoRespStructKls

    def __init__(self):

        self.IdtOTADeltaInfoRespStruct = IdtOTADeltaInfoRespStructKls()
