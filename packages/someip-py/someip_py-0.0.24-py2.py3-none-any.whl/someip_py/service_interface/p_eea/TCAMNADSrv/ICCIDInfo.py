from someip_py.codec import *


class IdtSimICCIDInfo(SomeIpPayload):

    SimNo: Uint8

    SimICCIDInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimICCIDInfo = SomeIpDynamicSizeString()


class IdtAllICCIDInfo(SomeIpPayload):

    IdtSimICCIDInfo: SomeIpDynamicSizeArray[IdtSimICCIDInfo]

    def __init__(self):

        self.IdtSimICCIDInfo = SomeIpDynamicSizeArray(IdtSimICCIDInfo)
