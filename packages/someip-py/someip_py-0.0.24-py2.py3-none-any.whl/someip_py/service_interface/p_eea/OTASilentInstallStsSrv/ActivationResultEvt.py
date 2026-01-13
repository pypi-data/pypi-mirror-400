from someip_py.codec import *


class IdtOTAActivationResultStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtOTAActivationResultStruct(SomeIpPayload):

    IdtOTAActivationResultStruct: IdtOTAActivationResultStructKls

    def __init__(self):

        self.IdtOTAActivationResultStruct = IdtOTAActivationResultStructKls()
