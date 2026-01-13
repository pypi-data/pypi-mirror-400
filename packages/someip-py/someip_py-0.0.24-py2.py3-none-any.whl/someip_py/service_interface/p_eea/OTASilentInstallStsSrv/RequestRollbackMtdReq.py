from someip_py.codec import *


class IDTRequestRollbackMtdReq(SomeIpPayload):

    IDTRequestRollbackMtdReq: Uint8

    def __init__(self):

        self.IDTRequestRollbackMtdReq = Uint8()
