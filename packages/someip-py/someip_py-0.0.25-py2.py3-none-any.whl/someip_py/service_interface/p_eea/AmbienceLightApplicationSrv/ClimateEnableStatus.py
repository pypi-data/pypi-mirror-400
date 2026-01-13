from someip_py.codec import *


class IdtModeEnablement(SomeIpPayload):

    IdtModeEnablement: Uint8

    def __init__(self):

        self.IdtModeEnablement = Uint8()
