from someip_py.codec import *


class IdtFaultItem(SomeIpPayload):

    UID: Uint32

    Operation: Uint8

    def __init__(self):

        self.UID = Uint32()

        self.Operation = Uint8()


class IdtADAlertFaultInfSts(SomeIpPayload):

    IdtFaultItem: SomeIpDynamicSizeArray[IdtFaultItem]

    def __init__(self):

        self.IdtFaultItem = SomeIpDynamicSizeArray(IdtFaultItem)
