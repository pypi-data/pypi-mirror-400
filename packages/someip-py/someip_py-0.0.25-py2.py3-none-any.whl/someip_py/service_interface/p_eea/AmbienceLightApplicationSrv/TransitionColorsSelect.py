from someip_py.codec import *


class IdtAmbColorGroup(SomeIpPayload):

    _include_struct_len = True

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtTransitionColorGroup(SomeIpPayload):

    _include_struct_len = True

    Zone: Uint8

    ColorA: IdtAmbColorGroup

    ColorB: IdtAmbColorGroup

    def __init__(self):

        self.Zone = Uint8()

        self.ColorA = IdtAmbColorGroup()

        self.ColorB = IdtAmbColorGroup()


class IdtTransitionColorAry(SomeIpPayload):

    IdtTransitionColorGroup: SomeIpDynamicSizeArray[IdtTransitionColorGroup]

    def __init__(self):

        self.IdtTransitionColorGroup = SomeIpDynamicSizeArray(IdtTransitionColorGroup)


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
