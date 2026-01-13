from someip_py.codec import *


class IdtStfnLvlCmd(SomeIpPayload):

    IdtStfnLvlCmd: Uint8

    def __init__(self):

        self.IdtStfnLvlCmd = Uint8()


class IdtReturnCode(SomeIpPayload):

    IdtReturnCode: Uint8

    def __init__(self):

        self.IdtReturnCode = Uint8()
