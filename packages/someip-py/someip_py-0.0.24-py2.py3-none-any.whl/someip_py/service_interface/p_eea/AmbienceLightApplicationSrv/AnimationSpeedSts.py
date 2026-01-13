from someip_py.codec import *


class IdtAnimationSpeedGrp(SomeIpPayload):

    Type: Uint8

    Speed: Uint8

    def __init__(self):

        self.Type = Uint8()

        self.Speed = Uint8()


class IdtAnimationSpeedAry(SomeIpPayload):

    IdtAnimationSpeedGrp: SomeIpDynamicSizeArray[IdtAnimationSpeedGrp]

    def __init__(self):

        self.IdtAnimationSpeedGrp = SomeIpDynamicSizeArray(IdtAnimationSpeedGrp)
