from someip_py.codec import *


class IdtSetLogLevel(SomeIpPayload):

    IdtSetLogLevel: Uint8

    def __init__(self):

        self.IdtSetLogLevel = Uint8()


class IdtRtnVal(SomeIpPayload):

    IdtRtnVal: Uint8

    def __init__(self):

        self.IdtRtnVal = Uint8()
