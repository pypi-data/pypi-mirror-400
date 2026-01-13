from someip_py.codec import *


class IdtSuspStfnLvlStsKls(SomeIpPayload):

    StfnLvlStsFL: Uint8

    StfnLvlStsFR: Uint8

    StfnLvlStsRL: Uint8

    StfnLvlStsRR: Uint8

    def __init__(self):

        self.StfnLvlStsFL = Uint8()

        self.StfnLvlStsFR = Uint8()

        self.StfnLvlStsRL = Uint8()

        self.StfnLvlStsRR = Uint8()


class IdtSuspStfnLvlSts(SomeIpPayload):

    IdtSuspStfnLvlSts: IdtSuspStfnLvlStsKls

    def __init__(self):

        self.IdtSuspStfnLvlSts = IdtSuspStfnLvlStsKls()
