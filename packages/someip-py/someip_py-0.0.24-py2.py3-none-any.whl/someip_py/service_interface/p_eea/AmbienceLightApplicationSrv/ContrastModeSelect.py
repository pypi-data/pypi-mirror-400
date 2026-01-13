from someip_py.codec import *


class IdtContrastMode(SomeIpPayload):

    IdtContrastMode: Uint8

    def __init__(self):

        self.IdtContrastMode = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
