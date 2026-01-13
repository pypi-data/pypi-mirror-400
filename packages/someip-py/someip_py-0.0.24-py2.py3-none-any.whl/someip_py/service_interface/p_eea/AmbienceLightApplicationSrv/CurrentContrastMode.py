from someip_py.codec import *


class IdtContrastMode(SomeIpPayload):

    IdtContrastMode: Uint8

    def __init__(self):

        self.IdtContrastMode = Uint8()
