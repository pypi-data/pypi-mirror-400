from someip_py.codec import *


class IdtSimIMEIInfo(SomeIpPayload):

    SimNo: Uint8

    SimIMEIInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimIMEIInfo = SomeIpDynamicSizeString()


class IdtAllIMEIInfo(SomeIpPayload):

    IdtSimIMEIInfo: SomeIpDynamicSizeArray[IdtSimIMEIInfo]

    def __init__(self):

        self.IdtSimIMEIInfo = SomeIpDynamicSizeArray(IdtSimIMEIInfo)
