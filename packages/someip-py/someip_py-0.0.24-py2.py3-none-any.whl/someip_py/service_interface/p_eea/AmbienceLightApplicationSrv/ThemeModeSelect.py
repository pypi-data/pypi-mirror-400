from someip_py.codec import *


class IdtThemeMode(SomeIpPayload):

    IdtThemeMode: Uint8

    def __init__(self):

        self.IdtThemeMode = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
