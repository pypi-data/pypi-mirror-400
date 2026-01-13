from someip_py.codec import *


class IdtSetMdmLog(SomeIpPayload):

    IdtSetMdmLog: Uint8

    def __init__(self):

        self.IdtSetMdmLog = Uint8()


class IdtRtnVal(SomeIpPayload):

    IdtRtnVal: Uint8

    def __init__(self):

        self.IdtRtnVal = Uint8()
