from someip_py.codec import *


class IdtTCAMIDInfo(SomeIpPayload):

    IdtTCAMIDInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.IdtTCAMIDInfo = SomeIpDynamicSizeString()
