from someip_py.codec import *


class IdtSimMainCardSts(SomeIpPayload):

    SimNo: Uint8

    SimMainCardSts: Bool

    def __init__(self):

        self.SimNo = Uint8()

        self.SimMainCardSts = Bool()


class IdtAllMainCardSts(SomeIpPayload):

    IdtSimMainCardSts: SomeIpDynamicSizeArray[IdtSimMainCardSts]

    def __init__(self):

        self.IdtSimMainCardSts = SomeIpDynamicSizeArray(IdtSimMainCardSts)
