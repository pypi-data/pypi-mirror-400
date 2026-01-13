from someip_py.codec import *


class IdtDampModeCmd(SomeIpPayload):

    IdtDampModeCmd: Uint8

    def __init__(self):

        self.IdtDampModeCmd = Uint8()


class IdtReturnCode(SomeIpPayload):

    IdtReturnCode: Uint8

    def __init__(self):

        self.IdtReturnCode = Uint8()
