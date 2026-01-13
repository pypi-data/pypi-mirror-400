from someip_py.codec import *


class IdtSimMSISDNInfo(SomeIpPayload):

    SimNo: Uint8

    SimMSISDNInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimMSISDNInfo = SomeIpDynamicSizeString()


class IdtAllMSISDNInfo(SomeIpPayload):

    IdtSimMSISDNInfo: SomeIpDynamicSizeArray[IdtSimMSISDNInfo]

    def __init__(self):

        self.IdtSimMSISDNInfo = SomeIpDynamicSizeArray(IdtSimMSISDNInfo)
