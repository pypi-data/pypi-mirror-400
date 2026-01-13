from someip_py.codec import *


class IdtAmbColorGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtIndividualColorGroup(SomeIpPayload):

    Number: Uint8

    Color: IdtAmbColorGroup

    def __init__(self):

        self.Number = Uint8()

        self.Color = IdtAmbColorGroup()


class IdtIndividualColorArray(SomeIpPayload):

    IdtIndividualColorGroup: SomeIpDynamicSizeArray[IdtIndividualColorGroup]

    def __init__(self):

        self.IdtIndividualColorGroup = SomeIpDynamicSizeArray(IdtIndividualColorGroup)


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
