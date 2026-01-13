from someip_py.codec import *


class IdtHznProfLongLRKls(SomeIpPayload):

    CyclicCounter: Uint8

    MessageType: Uint8

    Offset: Uint16

    PathIndex: Uint8

    ProfileType: Uint8

    Value: Uint32

    Retransmission: Uint8

    Update: Uint8

    ControlPoint: Uint8

    def __init__(self):

        self.CyclicCounter = Uint8()

        self.MessageType = Uint8()

        self.Offset = Uint16()

        self.PathIndex = Uint8()

        self.ProfileType = Uint8()

        self.Value = Uint32()

        self.Retransmission = Uint8()

        self.Update = Uint8()

        self.ControlPoint = Uint8()


class IdtHznProfLongLR(SomeIpPayload):

    IdtHznProfLongLR: IdtHznProfLongLRKls

    def __init__(self):

        self.IdtHznProfLongLR = IdtHznProfLongLRKls()
