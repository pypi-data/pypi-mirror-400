from someip_py.codec import *


class IdtAmbColorGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtContrastModeColor(SomeIpPayload):

    Mode: Uint8

    Color1: IdtAmbColorGroup

    Color2: IdtAmbColorGroup

    def __init__(self):

        self.Mode = Uint8()

        self.Color1 = IdtAmbColorGroup()

        self.Color2 = IdtAmbColorGroup()


class IdtContrastModeColorArray(SomeIpPayload):

    IdtContrastModeColor: SomeIpDynamicSizeArray[IdtContrastModeColor]

    def __init__(self):

        self.IdtContrastModeColor = SomeIpDynamicSizeArray(IdtContrastModeColor)
