from someip_py.codec import *


class IdtInstallProgressRespStructKls(SomeIpPayload):

    UUID: SomeIpDynamicSizeString

    Isotimestamp: SomeIpDynamicSizeString

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.UUID = SomeIpDynamicSizeString()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtInstallProgressRespStruct(SomeIpPayload):

    IdtInstallProgressRespStruct: IdtInstallProgressRespStructKls

    def __init__(self):

        self.IdtInstallProgressRespStruct = IdtInstallProgressRespStructKls()
