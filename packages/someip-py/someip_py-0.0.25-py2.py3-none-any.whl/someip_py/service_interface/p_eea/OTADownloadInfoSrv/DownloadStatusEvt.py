from someip_py.codec import *


class IdtOTADownloadStatusStructKls(SomeIpPayload):

    _include_struct_len = True

    InstallationorderUUID: SomeIpDynamicSizeString

    Isotimestamp: SomeIpDynamicSizeString

    Downloadsize: Uint32

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.InstallationorderUUID = SomeIpDynamicSizeString()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Downloadsize = Uint32()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtOTADownloadStatusStruct(SomeIpPayload):

    IdtOTADownloadStatusStruct: IdtOTADownloadStatusStructKls

    def __init__(self):

        self.IdtOTADownloadStatusStruct = IdtOTADownloadStatusStructKls()
