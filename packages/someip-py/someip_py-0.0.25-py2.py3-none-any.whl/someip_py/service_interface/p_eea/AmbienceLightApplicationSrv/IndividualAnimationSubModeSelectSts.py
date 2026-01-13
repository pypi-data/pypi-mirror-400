from someip_py.codec import *


class IdtIndividualAnimationSubMode(SomeIpPayload):

    IdtIndividualAnimationSubMode: Uint8

    def __init__(self):

        self.IdtIndividualAnimationSubMode = Uint8()
