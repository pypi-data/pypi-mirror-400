from someip_py.codec import *


class IdtIndividualAnimationType(SomeIpPayload):

    IdtIndividualAnimationType: Uint8

    def __init__(self):

        self.IdtIndividualAnimationType = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
