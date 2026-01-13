from someip_py.codec import *


class IdtRVDCAssignmentNotificaitonKls(SomeIpPayload):

    Maid: Uint32

    Maversion: Uint32

    Isotimestamp: SomeIpDynamicSizeString

    Newstatus: SomeIpDynamicSizeString

    Reason: SomeIpDynamicSizeString

    def __init__(self):

        self.Maid = Uint32()

        self.Maversion = Uint32()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Newstatus = SomeIpDynamicSizeString()

        self.Reason = SomeIpDynamicSizeString()


class IdtRVDCAssignmentNotificaiton(SomeIpPayload):

    IdtRVDCAssignmentNotificaiton: IdtRVDCAssignmentNotificaitonKls

    def __init__(self):

        self.IdtRVDCAssignmentNotificaiton = IdtRVDCAssignmentNotificaitonKls()


class IdtRtnVal(SomeIpPayload):

    IdtRtnVal: Uint8

    def __init__(self):

        self.IdtRtnVal = Uint8()
