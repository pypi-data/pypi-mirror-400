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


class IdtIndividualSingleColorCollectKls(SomeIpPayload):
    _has_dynamic_size = True
    _include_struct_len = True

    Number: Uint8

    ColorVec: SomeIpDynamicSizeArray[IdtAmbColorGroup]

    def __init__(self):

        self.Number = Uint8()

        self.ColorVec = SomeIpDynamicSizeArray(IdtAmbColorGroup)


class IdtIndividualSingleColorCollect(SomeIpPayload):

    IdtIndividualSingleColorCollect: IdtIndividualSingleColorCollectKls

    def __init__(self):

        self.IdtIndividualSingleColorCollect = IdtIndividualSingleColorCollectKls()
