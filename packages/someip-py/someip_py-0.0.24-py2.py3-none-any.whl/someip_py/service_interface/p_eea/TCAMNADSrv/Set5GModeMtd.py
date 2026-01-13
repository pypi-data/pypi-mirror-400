from someip_py.codec import *


class IdtFIVEGMode(SomeIpPayload):

    IdtFIVEGMode: Uint8

    def __init__(self):

        self.IdtFIVEGMode = Uint8()


class IdtRtnVal(SomeIpPayload):

    IdtRtnVal: Uint8

    def __init__(self):

        self.IdtRtnVal = Uint8()
