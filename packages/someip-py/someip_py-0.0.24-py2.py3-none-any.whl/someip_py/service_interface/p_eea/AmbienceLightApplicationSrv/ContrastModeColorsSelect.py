from someip_py.codec import *


class IdtContrastMode(SomeIpPayload):

    IdtContrastMode: Uint8

    def __init__(self):

        self.IdtContrastMode = Uint8()


class IdtAmbColorGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtContrastColorGroup(SomeIpPayload):

    Number: Uint8

    Color: IdtAmbColorGroup

    def __init__(self):

        self.Number = Uint8()

        self.Color = IdtAmbColorGroup()


class IdtContrastColorArray(SomeIpPayload):

    IdtContrastColorGroup: SomeIpDynamicSizeArray[IdtContrastColorGroup]

    def __init__(self):

        self.IdtContrastColorGroup = SomeIpDynamicSizeArray(IdtContrastColorGroup)


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
