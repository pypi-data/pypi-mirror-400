from someip_py.codec import *


class IdtHznProfShoKls(SomeIpPayload):

    CyclicCounter: Uint8

    MessageType: Uint8

    Offset: Uint16

    PathIndex: Uint8

    ProfileType: Uint8

    Value: Uint32

    Accuracy: Uint8

    Distance: Uint16

    ControlPoint: Uint8

    Retransmission: Uint8

    Update: Uint8

    Value1: Uint32

    def __init__(self):

        self.CyclicCounter = Uint8()

        self.MessageType = Uint8()

        self.Offset = Uint16()

        self.PathIndex = Uint8()

        self.ProfileType = Uint8()

        self.Value = Uint32()

        self.Accuracy = Uint8()

        self.Distance = Uint16()

        self.ControlPoint = Uint8()

        self.Retransmission = Uint8()

        self.Update = Uint8()

        self.Value1 = Uint32()


class IdtHznProfSho(SomeIpPayload):

    IdtHznProfSho: IdtHznProfShoKls

    def __init__(self):

        self.IdtHznProfSho = IdtHznProfShoKls()
