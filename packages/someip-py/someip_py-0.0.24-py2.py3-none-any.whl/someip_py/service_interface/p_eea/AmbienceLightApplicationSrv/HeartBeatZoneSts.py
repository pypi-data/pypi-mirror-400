from someip_py.codec import *


class IdtCustomizedZone(SomeIpPayload):

    IdtCustomizedZone: Uint8

    def __init__(self):

        self.IdtCustomizedZone = Uint8()
