from someip_py.codec import *


class IdtOTARequestActRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtOTARequestActRespStruct(SomeIpPayload):

    IdtOTARequestActRespStruct: IdtOTARequestActRespStructKls

    def __init__(self):

        self.IdtOTARequestActRespStruct = IdtOTARequestActRespStructKls()
