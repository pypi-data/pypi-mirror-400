from someip_py.codec import *


class IdtColorsTipType(SomeIpPayload):

    IdtColorsTipType: Uint8

    def __init__(self):

        self.IdtColorsTipType = Uint8()


class IdtAmbColorGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtColorsTipArray(SomeIpPayload):

    IdtAmbColorGroup: SomeIpDynamicSizeArray[IdtAmbColorGroup]

    def __init__(self):

        self.IdtAmbColorGroup = SomeIpDynamicSizeArray(IdtAmbColorGroup)


class IdtAmbienceAppReturnCode(SomeIpPayload):

    IdtAmbienceAppReturnCode: Uint8

    def __init__(self):

        self.IdtAmbienceAppReturnCode = Uint8()
