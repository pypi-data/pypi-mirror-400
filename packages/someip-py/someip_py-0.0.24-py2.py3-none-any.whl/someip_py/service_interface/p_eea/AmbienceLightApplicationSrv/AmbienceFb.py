from someip_py.codec import *


class IdtAmbienceAry(SomeIpPayload):

    IdtAmbienceColor: SomeIpDynamicSizeArray[Uint8]

    def __init__(self):

        self.IdtAmbienceColor = SomeIpDynamicSizeArray(Uint8)
