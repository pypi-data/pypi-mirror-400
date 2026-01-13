from someip_py.codec import *


class IdtAmbColorGroupKls(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtAmbColorGroup(SomeIpPayload):

    IdtAmbColorGroup: IdtAmbColorGroupKls

    def __init__(self):

        self.IdtAmbColorGroup = IdtAmbColorGroupKls()
