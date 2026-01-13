from someip_py.codec import *


class IdtAmbientModeSelect(SomeIpPayload):

    IdtAmbientModeSelect: Uint8

    def __init__(self):

        self.IdtAmbientModeSelect = Uint8()
