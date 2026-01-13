from someip_py.codec import *


class IdtHeiInhbSts(SomeIpPayload):

    IdtHeiInhbSts: Uint8

    def __init__(self):

        self.IdtHeiInhbSts = Uint8()
