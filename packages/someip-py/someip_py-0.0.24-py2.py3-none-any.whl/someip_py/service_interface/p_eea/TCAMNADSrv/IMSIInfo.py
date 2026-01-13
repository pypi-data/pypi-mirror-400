from someip_py.codec import *


class IdtSimIMSIInfo(SomeIpPayload):

    SimNo: Uint8

    SimIMSIInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimIMSIInfo = SomeIpDynamicSizeString()


class IdtAllIMSIInfo(SomeIpPayload):

    IdtSimIMSIInfo: SomeIpDynamicSizeArray[IdtSimIMSIInfo]

    def __init__(self):

        self.IdtSimIMSIInfo = SomeIpDynamicSizeArray(IdtSimIMSIInfo)
