from someip_py.codec import *


class IdtChannelType(SomeIpPayload):

    IdtChannelType: Uint8

    def __init__(self):

        self.IdtChannelType = Uint8()
