from someip_py.codec import *


class IdtCustomizedZone(SomeIpPayload):

    IdtCustomizedZone: Uint8

    def __init__(self):

        self.IdtCustomizedZone = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
