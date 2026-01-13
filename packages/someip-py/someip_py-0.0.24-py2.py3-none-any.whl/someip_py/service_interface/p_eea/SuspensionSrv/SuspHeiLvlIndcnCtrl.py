from someip_py.codec import *


class IdtSuspHeiLvlIndcnKls(SomeIpPayload):

    SuspHeiLvlIndcnVal: Uint8

    IsOccupied: Uint8

    SuspCtrlPriority: Uint8

    def __init__(self):

        self.SuspHeiLvlIndcnVal = Uint8()

        self.IsOccupied = Uint8()

        self.SuspCtrlPriority = Uint8()


class IdtSuspHeiLvlIndcn(SomeIpPayload):

    IdtSuspHeiLvlIndcn: IdtSuspHeiLvlIndcnKls

    def __init__(self):

        self.IdtSuspHeiLvlIndcn = IdtSuspHeiLvlIndcnKls()


class IdtReturnCode(SomeIpPayload):

    IdtReturnCode: Uint8

    def __init__(self):

        self.IdtReturnCode = Uint8()
