from someip_py.codec import *


class IdtGidGroup(SomeIpPayload):

    IdtProfileGidValue: SomeIpDynamicSizeArray[SomeIpDynamicSizeString]

    def __init__(self):

        self.IdtProfileGidValue = SomeIpDynamicSizeArray(SomeIpDynamicSizeString)
