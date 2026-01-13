from someip_py.codec import *


class IdtHznProfLongKls(SomeIpPayload):

    CyclicCounter: Uint8

    MessageType: Uint8

    Offset: Uint16

    PathIndex: Uint8

    ProfileType: Uint8

    ControlPoint: Uint8

    Retransmission: Uint8

    Update: Uint8

    Value: Uint32

    def __init__(self):

        self.CyclicCounter = Uint8()

        self.MessageType = Uint8()

        self.Offset = Uint16()

        self.PathIndex = Uint8()

        self.ProfileType = Uint8()

        self.ControlPoint = Uint8()

        self.Retransmission = Uint8()

        self.Update = Uint8()

        self.Value = Uint32()


class IdtHznProfLong(SomeIpPayload):

    IdtHznProfLong: IdtHznProfLongKls

    def __init__(self):

        self.IdtHznProfLong = IdtHznProfLongKls()
