from someip_py.codec import *


class IdtAnimationSelectType(SomeIpPayload):

    IdtAnimationSelectType: Uint8

    def __init__(self):

        self.IdtAnimationSelectType = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
