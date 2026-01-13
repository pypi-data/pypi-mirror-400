from someip_py.codec import *


class IdtInstallationStatusStructKls(SomeIpPayload):

    UUID: SomeIpDynamicSizeString

    isotimestamp: SomeIpDynamicSizeString

    NewStatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.UUID = SomeIpDynamicSizeString()

        self.isotimestamp = SomeIpDynamicSizeString()

        self.NewStatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtInstallationStatusStruct(SomeIpPayload):

    IdtInstallationStatusStruct: IdtInstallationStatusStructKls

    def __init__(self):

        self.IdtInstallationStatusStruct = IdtInstallationStatusStructKls()
