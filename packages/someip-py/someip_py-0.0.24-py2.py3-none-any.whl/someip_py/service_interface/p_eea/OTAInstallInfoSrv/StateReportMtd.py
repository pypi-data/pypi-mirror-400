from someip_py.codec import *


class IdtOTAStateMechanismReportStructKls(SomeIpPayload):

    UUID: SomeIpDynamicSizeString

    Isotimestamp: SomeIpDynamicSizeString

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.UUID = SomeIpDynamicSizeString()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtOTAStateMechanismReportStruct(SomeIpPayload):

    IdtOTAStateMechanismReportStruct: IdtOTAStateMechanismReportStructKls

    def __init__(self):

        self.IdtOTAStateMechanismReportStruct = IdtOTAStateMechanismReportStructKls()
