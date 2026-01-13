from someip_py.codec import *


class IdtAmbColorGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtAmbDoubleColorGrp(SomeIpPayload):

    ColorA: IdtAmbColorGroup

    ColorB: IdtAmbColorGroup

    def __init__(self):

        self.ColorA = IdtAmbColorGroup()

        self.ColorB = IdtAmbColorGroup()


class IdtIndividualDoubleColorCollectKls(SomeIpPayload):
    _has_dynamic_size = True

    Number: Uint8

    DoubleColorVec: SomeIpDynamicSizeArray[IdtAmbDoubleColorGrp]

    def __init__(self):

        self.Number = Uint8()

        self.DoubleColorVec = SomeIpDynamicSizeArray(IdtAmbDoubleColorGrp)


class IdtIndividualDoubleColorCollect(SomeIpPayload):

    IdtIndividualDoubleColorCollect: IdtIndividualDoubleColorCollectKls

    def __init__(self):

        self.IdtIndividualDoubleColorCollect = IdtIndividualDoubleColorCollectKls()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
