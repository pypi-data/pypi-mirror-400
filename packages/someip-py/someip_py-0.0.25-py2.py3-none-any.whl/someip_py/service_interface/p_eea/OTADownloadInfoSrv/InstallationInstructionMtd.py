from someip_py.codec import *


class IdtInstallationInstructionsStruct(SomeIpPayload):

    _include_struct_len = True

    Installationinstructionsversion: SomeIpDynamicSizeString

    Bssid: SomeIpDynamicSizeString

    Displayedversion: SomeIpDynamicSizeString

    TargetECUNum: Uint8

    MaximumParallelECUNum: Uint8

    Requiredpreparationtime: Uint32

    Expectedinstallationtime: Uint32

    Area1112securitycode: SomeIpDynamicSizeString

    Operationsequence: Uint32

    def __init__(self):

        self.Installationinstructionsversion = SomeIpDynamicSizeString()

        self.Bssid = SomeIpDynamicSizeString()

        self.Displayedversion = SomeIpDynamicSizeString()

        self.TargetECUNum = Uint8()

        self.MaximumParallelECUNum = Uint8()

        self.Requiredpreparationtime = Uint32()

        self.Expectedinstallationtime = Uint32()

        self.Area1112securitycode = SomeIpDynamicSizeString()

        self.Operationsequence = Uint32()


class IdtOTAWriteInstallationInstructionStructKls(SomeIpPayload):

    _include_struct_len = True

    InstallationorderUUID: SomeIpDynamicSizeString

    Ecuremaining: Uint8

    InstallationInstructionsStruct: IdtInstallationInstructionsStruct

    def __init__(self):

        self.InstallationorderUUID = SomeIpDynamicSizeString()

        self.Ecuremaining = Uint8()

        self.InstallationInstructionsStruct = IdtInstallationInstructionsStruct()


class IdtOTAWriteInstallationInstructionStruct(SomeIpPayload):

    IdtOTAWriteInstallationInstructionStruct: IdtOTAWriteInstallationInstructionStructKls

    def __init__(self):

        self.IdtOTAWriteInstallationInstructionStruct = (
            IdtOTAWriteInstallationInstructionStructKls()
        )


class IdtOTAWriteInstallationInstructionRespKls(SomeIpPayload):

    _include_struct_len = True

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtOTAWriteInstallationInstructionResp(SomeIpPayload):

    IdtOTAWriteInstallationInstructionResp: IdtOTAWriteInstallationInstructionRespKls

    def __init__(self):

        self.IdtOTAWriteInstallationInstructionResp = (
            IdtOTAWriteInstallationInstructionRespKls()
        )
