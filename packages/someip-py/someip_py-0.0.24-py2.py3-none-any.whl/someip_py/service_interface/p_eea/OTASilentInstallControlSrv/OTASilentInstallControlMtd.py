from someip_py.codec import *


class IdtOTASilentInstallControlStructKls(SomeIpPayload):

    UUID: SomeIpDynamicSizeString

    Isotimestamp: SomeIpDynamicSizeString

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.UUID = SomeIpDynamicSizeString()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtOTASilentInstallControlStruct(SomeIpPayload):

    IdtOTASilentInstallControlStruct: IdtOTASilentInstallControlStructKls

    def __init__(self):

        self.IdtOTASilentInstallControlStruct = IdtOTASilentInstallControlStructKls()


class IdtOTASilentInstallControlRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RtnVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RtnVal = Uint8()


class IdtOTASilentInstallControlRespStruct(SomeIpPayload):

    IdtOTASilentInstallControlRespStruct: IdtOTASilentInstallControlRespStructKls

    def __init__(self):

        self.IdtOTASilentInstallControlRespStruct = (
            IdtOTASilentInstallControlRespStructKls()
        )
