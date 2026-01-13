from someip_py.codec import *


class IdtAmbientModeSelect(SomeIpPayload):

    IdtAmbientModeSelect: Uint8

    def __init__(self):

        self.IdtAmbientModeSelect = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
