from someip_py.codec import *


class IdtIndividualAnimationType(SomeIpPayload):

    IdtIndividualAnimationType: Uint8

    def __init__(self):

        self.IdtIndividualAnimationType = Uint8()
