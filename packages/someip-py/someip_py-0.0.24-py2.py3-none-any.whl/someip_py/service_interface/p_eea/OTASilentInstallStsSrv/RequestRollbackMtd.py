from someip_py.codec import *


class IdtOTARequestRollbackStruct(SomeIpPayload):

    IdtOTARequestRollbackStruct: Uint8

    def __init__(self):

        self.IdtOTARequestRollbackStruct = Uint8()


class IdtOTASignatureCertificateRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RtnVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RtnVal = Uint8()


class IdtOTASignatureCertificateRespStruct(SomeIpPayload):

    IdtOTASignatureCertificateRespStruct: IdtOTASignatureCertificateRespStructKls

    def __init__(self):

        self.IdtOTASignatureCertificateRespStruct = (
            IdtOTASignatureCertificateRespStructKls()
        )
