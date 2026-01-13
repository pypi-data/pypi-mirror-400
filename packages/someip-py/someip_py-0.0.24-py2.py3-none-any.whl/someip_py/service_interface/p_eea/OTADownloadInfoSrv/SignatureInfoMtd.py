from someip_py.codec import *


class IdtAssignfileinfoStruct(SomeIpPayload):

    FileName: SomeIpDynamicSizeString

    Flashgroupid: Uint32

    DownloadType: SomeIpDynamicSizeString

    FileEncryptionType: Uint8

    Validtime: SomeIpDynamicSizeString

    Validdate: SomeIpDynamicSizeString

    Softwarepartsignature: SomeIpDynamicSizeString

    Filechecksum: SomeIpDynamicSizeString

    def __init__(self):

        self.FileName = SomeIpDynamicSizeString()

        self.Flashgroupid = Uint32()

        self.DownloadType = SomeIpDynamicSizeString()

        self.FileEncryptionType = Uint8()

        self.Validtime = SomeIpDynamicSizeString()

        self.Validdate = SomeIpDynamicSizeString()

        self.Softwarepartsignature = SomeIpDynamicSizeString()

        self.Filechecksum = SomeIpDynamicSizeString()


class IdtOTASetAssignmentFileInfoStructKls(SomeIpPayload):
    _has_dynamic_size = True

    InstallationorderUUID: SomeIpDynamicSizeString

    Ecuremaining: Uint8

    EcuAddressOTA: SomeIpDynamicSizeString

    LastSegment: Uint8

    AssignfileinfoArraytyp: SomeIpDynamicSizeArray[IdtAssignfileinfoStruct]

    def __init__(self):

        self.InstallationorderUUID = SomeIpDynamicSizeString()

        self.Ecuremaining = Uint8()

        self.EcuAddressOTA = SomeIpDynamicSizeString()

        self.LastSegment = Uint8()

        self.AssignfileinfoArraytyp = SomeIpDynamicSizeArray(IdtAssignfileinfoStruct)


class IdtOTASetAssignmentFileInfoStruct(SomeIpPayload):

    IdtOTASetAssignmentFileInfoStruct: IdtOTASetAssignmentFileInfoStructKls

    def __init__(self):

        self.IdtOTASetAssignmentFileInfoStruct = IdtOTASetAssignmentFileInfoStructKls()


class IdtOTASetAssignmentFileInfoRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtOTASetAssignmentFileInfoRespStruct(SomeIpPayload):

    IdtOTASetAssignmentFileInfoRespStruct: IdtOTASetAssignmentFileInfoRespStructKls

    def __init__(self):

        self.IdtOTASetAssignmentFileInfoRespStruct = (
            IdtOTASetAssignmentFileInfoRespStructKls()
        )
