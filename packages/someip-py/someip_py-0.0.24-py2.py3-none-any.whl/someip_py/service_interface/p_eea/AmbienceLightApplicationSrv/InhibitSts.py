from someip_py.codec import *


class IdtAmbInhibitStsStrKls(SomeIpPayload):
    _has_dynamic_size = True

    SrcGrp: SomeIpDynamicSizeArray[Uint8]

    Type: Uint8

    def __init__(self):

        self.SrcGrp = SomeIpDynamicSizeArray(Uint8)

        self.Type = Uint8()


class IdtAmbInhibitStsStr(SomeIpPayload):

    IdtAmbInhibitStsStr: IdtAmbInhibitStsStrKls

    def __init__(self):

        self.IdtAmbInhibitStsStr = IdtAmbInhibitStsStrKls()
