from someip_py.codec import *


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
