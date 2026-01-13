from someip_py.codec import *


class IdtSilentInstallStsStructKls(SomeIpPayload):

    UUID: SomeIpDynamicSizeString

    Isotimestamp: SomeIpDynamicSizeString

    Silentinstallsize: Uint32

    Newstatus: SomeIpDynamicSizeString

    Currentareastatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.UUID = SomeIpDynamicSizeString()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Silentinstallsize = Uint32()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Currentareastatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtSilentInstallStsStruct(SomeIpPayload):

    IdtSilentInstallStsStruct: IdtSilentInstallStsStructKls

    def __init__(self):

        self.IdtSilentInstallStsStruct = IdtSilentInstallStsStructKls()
