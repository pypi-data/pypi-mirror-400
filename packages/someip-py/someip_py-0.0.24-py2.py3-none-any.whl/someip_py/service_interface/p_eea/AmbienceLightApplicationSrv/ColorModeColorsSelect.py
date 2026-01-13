from someip_py.codec import *


class IdtColorMode(SomeIpPayload):

    IdtColorMode: Uint8

    def __init__(self):

        self.IdtColorMode = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
