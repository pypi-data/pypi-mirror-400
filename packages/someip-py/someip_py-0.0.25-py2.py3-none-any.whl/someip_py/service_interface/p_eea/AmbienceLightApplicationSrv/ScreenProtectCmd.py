from someip_py.codec import *


class IdtAmbScreenProtect(SomeIpPayload):

    IdtAmbScreenProtect: Uint8

    def __init__(self):

        self.IdtAmbScreenProtect = Uint8()


class IdtAmbienceAppReturnCode(SomeIpPayload):

    IdtAmbienceAppReturnCode: Uint8

    def __init__(self):

        self.IdtAmbienceAppReturnCode = Uint8()
