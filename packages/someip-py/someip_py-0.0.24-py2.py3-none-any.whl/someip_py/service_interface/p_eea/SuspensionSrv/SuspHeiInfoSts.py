from someip_py.codec import *


class IdtSuspHeiSts(SomeIpPayload):

    SuspHeiVal: Float32

    SuspHeiValQf: Uint8

    SuspHeiMoveSts: Uint8

    def __init__(self):

        self.SuspHeiVal = Float32()

        self.SuspHeiValQf = Uint8()

        self.SuspHeiMoveSts = Uint8()


class IdtSuspHeiInfoStsKls(SomeIpPayload):
    _has_dynamic_size = True

    SuspCtrlSource: Uint8

    VehSuspHeiMoveSts: Uint8

    SuspHeiStsFL: IdtSuspHeiSts

    SuspHeiStsFR: IdtSuspHeiSts

    SuspHeiStsRL: IdtSuspHeiSts

    SuspHeiStsRR: IdtSuspHeiSts

    SuspHeiCtrlFailReasonStsAry: SomeIpDynamicSizeArray[Uint8]

    def __init__(self):

        self.SuspCtrlSource = Uint8()

        self.VehSuspHeiMoveSts = Uint8()

        self.SuspHeiStsFL = IdtSuspHeiSts()

        self.SuspHeiStsFR = IdtSuspHeiSts()

        self.SuspHeiStsRL = IdtSuspHeiSts()

        self.SuspHeiStsRR = IdtSuspHeiSts()

        self.SuspHeiCtrlFailReasonStsAry = SomeIpDynamicSizeArray(Uint8)


class IdtSuspHeiInfoSts(SomeIpPayload):

    IdtSuspHeiInfoSts: IdtSuspHeiInfoStsKls

    def __init__(self):

        self.IdtSuspHeiInfoSts = IdtSuspHeiInfoStsKls()
