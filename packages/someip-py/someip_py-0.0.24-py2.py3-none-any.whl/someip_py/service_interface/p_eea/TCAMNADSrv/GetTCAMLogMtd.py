from someip_py.codec import *


class IdtGetLogRespStructKls(SomeIpPayload):

    GetLogResponse: Uint8

    RtnVal: Uint8

    def __init__(self):

        self.GetLogResponse = Uint8()

        self.RtnVal = Uint8()


class IdtGetLogRespStruct(SomeIpPayload):

    IdtGetLogRespStruct: IdtGetLogRespStructKls

    def __init__(self):

        self.IdtGetLogRespStruct = IdtGetLogRespStructKls()
