from someip_py.codec import *


class IdtSetFlyMode(SomeIpPayload):

    IdtSetFlyMode: Uint8

    def __init__(self):

        self.IdtSetFlyMode = Uint8()


class IdtRtnVal(SomeIpPayload):

    IdtRtnVal: Uint8

    def __init__(self):

        self.IdtRtnVal = Uint8()
