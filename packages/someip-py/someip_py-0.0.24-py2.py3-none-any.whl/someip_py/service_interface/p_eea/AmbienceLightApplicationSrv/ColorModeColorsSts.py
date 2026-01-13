from someip_py.codec import *


class IdtColorMode(SomeIpPayload):

    IdtColorMode: Uint8

    def __init__(self):

        self.IdtColorMode = Uint8()
