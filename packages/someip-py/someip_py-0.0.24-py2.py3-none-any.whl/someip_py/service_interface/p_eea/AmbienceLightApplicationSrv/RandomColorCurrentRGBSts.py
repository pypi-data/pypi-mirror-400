from someip_py.codec import *


class IdtAmbColorIntensGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    Intensity: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()

        self.Intensity = Uint8()


class IdtRandomColorGroup(SomeIpPayload):

    Zone: Uint8

    RandomColor: IdtAmbColorIntensGroup

    def __init__(self):

        self.Zone = Uint8()

        self.RandomColor = IdtAmbColorIntensGroup()


class IdtRandomColorGrpAry(SomeIpPayload):

    IdtRandomColorGroup: SomeIpDynamicSizeArray[IdtRandomColorGroup]

    def __init__(self):

        self.IdtRandomColorGroup = SomeIpDynamicSizeArray(IdtRandomColorGroup)
