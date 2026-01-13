from someip_py.codec import *


class IdtAmbColorGroup(SomeIpPayload):

    Red: Uint8

    Green: Uint8

    Blue: Uint8

    def __init__(self):

        self.Red = Uint8()

        self.Green = Uint8()

        self.Blue = Uint8()


class IdtRhythmColorsTipKls(SomeIpPayload):

    Left: IdtAmbColorGroup

    Middle: IdtAmbColorGroup

    Right: IdtAmbColorGroup

    def __init__(self):

        self.Left = IdtAmbColorGroup()

        self.Middle = IdtAmbColorGroup()

        self.Right = IdtAmbColorGroup()


class IdtRhythmColorsTip(SomeIpPayload):

    IdtRhythmColorsTip: IdtRhythmColorsTipKls

    def __init__(self):

        self.IdtRhythmColorsTip = IdtRhythmColorsTipKls()


class IdtAmbienceAppReturnCode(SomeIpPayload):

    IdtAmbienceAppReturnCode: Uint8

    def __init__(self):

        self.IdtAmbienceAppReturnCode = Uint8()
