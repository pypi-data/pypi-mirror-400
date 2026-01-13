from someip_py.codec import *


class IdtProfileGidValue(SomeIpPayload):

    IdtProfileGidValue: SomeIpDynamicSizeString

    def __init__(self):

        self.IdtProfileGidValue = SomeIpDynamicSizeString()
