from someip_py.codec import *


class IdtSuspHeiInhbCmd(SomeIpPayload):

    IdtSuspHeiInhbCmd: Uint8

    def __init__(self):

        self.IdtSuspHeiInhbCmd = Uint8()


class IdtReturnCode(SomeIpPayload):

    IdtReturnCode: Uint8

    def __init__(self):

        self.IdtReturnCode = Uint8()
