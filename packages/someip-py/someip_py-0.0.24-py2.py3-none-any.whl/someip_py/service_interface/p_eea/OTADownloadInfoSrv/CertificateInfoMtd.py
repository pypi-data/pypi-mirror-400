from someip_py.codec import *


class IdtOTASignatureCertificateStructKls(SomeIpPayload):

    OTASignatureCertificateStr: SomeIpDynamicSizeString

    OCSPRespData: SomeIpDynamicSizeString

    def __init__(self):

        self.OTASignatureCertificateStr = SomeIpDynamicSizeString()

        self.OCSPRespData = SomeIpDynamicSizeString()


class IdtOTASignatureCertificateStruct(SomeIpPayload):

    IdtOTASignatureCertificateStruct: IdtOTASignatureCertificateStructKls

    def __init__(self):

        self.IdtOTASignatureCertificateStruct = IdtOTASignatureCertificateStructKls()


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
