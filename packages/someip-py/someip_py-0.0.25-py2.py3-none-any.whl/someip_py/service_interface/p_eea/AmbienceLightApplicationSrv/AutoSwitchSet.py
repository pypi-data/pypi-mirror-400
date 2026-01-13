from someip_py.codec import *


class IdtAmbAutoSwtSet(SomeIpPayload):

    IdtAmbAutoSwtSet: Uint8

    def __init__(self):

        self.IdtAmbAutoSwtSet = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
