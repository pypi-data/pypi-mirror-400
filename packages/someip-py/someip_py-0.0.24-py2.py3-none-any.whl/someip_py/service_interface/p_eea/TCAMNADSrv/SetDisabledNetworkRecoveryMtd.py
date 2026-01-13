from someip_py.codec import *


class IdtSetDisabledNetworkRecovery(SomeIpPayload):

    IdtSetDisabledNetworkRecovery: Uint8

    def __init__(self):

        self.IdtSetDisabledNetworkRecovery = Uint8()


class IdtRtnVal(SomeIpPayload):

    IdtRtnVal: Uint8

    def __init__(self):

        self.IdtRtnVal = Uint8()
