from someip_py.codec import *


class IdtADHealthStsKls(SomeIpPayload):

    ChannelType: Uint8

    ADHealthTimeStamp: Uint64

    def __init__(self):

        self.ChannelType = Uint8()

        self.ADHealthTimeStamp = Uint64()


class IdtADHealthSts(SomeIpPayload):

    IdtADHealthSts: IdtADHealthStsKls

    def __init__(self):

        self.IdtADHealthSts = IdtADHealthStsKls()
