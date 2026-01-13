from someip_py.codec import *


class IdtAnimationSelectType(SomeIpPayload):

    IdtAnimationSelectType: Uint8

    def __init__(self):

        self.IdtAnimationSelectType = Uint8()
