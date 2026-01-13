from someip_py.codec import *


class IdtSetEnvironmentVariable(SomeIpPayload):

    IdtSetEnvironmentVariable: Uint8

    def __init__(self):

        self.IdtSetEnvironmentVariable = Uint8()


class IdtRtnVal(SomeIpPayload):

    IdtRtnVal: Uint8

    def __init__(self):

        self.IdtRtnVal = Uint8()
