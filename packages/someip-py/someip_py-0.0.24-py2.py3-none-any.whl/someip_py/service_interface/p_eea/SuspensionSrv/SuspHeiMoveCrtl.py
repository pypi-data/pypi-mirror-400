from someip_py.codec import *


class IdtHeiMoveCrtl(SomeIpPayload):

    IdtHeiMoveCrtl: Uint8

    def __init__(self):

        self.IdtHeiMoveCrtl = Uint8()


class IdtReturnCode(SomeIpPayload):

    IdtReturnCode: Uint8

    def __init__(self):

        self.IdtReturnCode = Uint8()
