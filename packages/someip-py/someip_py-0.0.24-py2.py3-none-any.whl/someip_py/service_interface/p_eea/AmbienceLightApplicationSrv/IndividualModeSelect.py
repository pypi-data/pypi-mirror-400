from someip_py.codec import *


class IdtIndividualMode(SomeIpPayload):

    IdtIndividualMode: Uint8

    def __init__(self):

        self.IdtIndividualMode = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
