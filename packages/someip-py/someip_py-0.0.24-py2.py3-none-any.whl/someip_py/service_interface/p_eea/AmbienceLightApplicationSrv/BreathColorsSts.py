from someip_py.codec import *


class IdtAmbColorGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtCustomizedColorGroup(SomeIpPayload):

    Zone: Uint8

    CustomizedColor: IdtAmbColorGroup

    def __init__(self):

        self.Zone = Uint8()

        self.CustomizedColor = IdtAmbColorGroup()


class IdtCustomizedColorAry(SomeIpPayload):

    IdtCustomizedColorGroup: SomeIpDynamicSizeArray[IdtCustomizedColorGroup]

    def __init__(self):

        self.IdtCustomizedColorGroup = SomeIpDynamicSizeArray(IdtCustomizedColorGroup)
