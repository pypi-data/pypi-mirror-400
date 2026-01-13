from someip_py.codec import *


class IdtPostInstallationInfoStructKls(SomeIpPayload):

    Installationorder: SomeIpDynamicSizeString

    Isotimestamp: SomeIpDynamicSizeString

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.Installationorder = SomeIpDynamicSizeString()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtPostInstallationInfoStruct(SomeIpPayload):

    IdtPostInstallationInfoStruct: IdtPostInstallationInfoStructKls

    def __init__(self):

        self.IdtPostInstallationInfoStruct = IdtPostInstallationInfoStructKls()


class IdtOTAAssignmentNotificationRespStructKls(SomeIpPayload):

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtOTAAssignmentNotificationRespStruct(SomeIpPayload):

    IdtOTAAssignmentNotificationRespStruct: IdtOTAAssignmentNotificationRespStructKls

    def __init__(self):

        self.IdtOTAAssignmentNotificationRespStruct = (
            IdtOTAAssignmentNotificationRespStructKls()
        )
