from someip_py.codec import *


class IdtHznEdgeKls(SomeIpPayload):

    CyclicCounter: Uint8

    ComplexIntersection: Uint8

    FunctionalRoadClass: Uint8

    LastStubAtOffset: Uint8

    MessageType: Uint8

    NumberOfLanesInDrivingDirection: Uint8

    EdgeOffset: Uint16

    PartOfCalculatedRoute: Uint8

    PathIndex: Uint8

    RelativeProbability: Uint8

    RightofWay: Uint8

    TurnAngle: Uint8

    Retransmission: Uint8

    Update: Uint8

    FormOfWay: Uint8

    NumberOfLanesInOppositeDirection: Uint8

    SubPathIndex: Uint8

    def __init__(self):

        self.CyclicCounter = Uint8()

        self.ComplexIntersection = Uint8()

        self.FunctionalRoadClass = Uint8()

        self.LastStubAtOffset = Uint8()

        self.MessageType = Uint8()

        self.NumberOfLanesInDrivingDirection = Uint8()

        self.EdgeOffset = Uint16()

        self.PartOfCalculatedRoute = Uint8()

        self.PathIndex = Uint8()

        self.RelativeProbability = Uint8()

        self.RightofWay = Uint8()

        self.TurnAngle = Uint8()

        self.Retransmission = Uint8()

        self.Update = Uint8()

        self.FormOfWay = Uint8()

        self.NumberOfLanesInOppositeDirection = Uint8()

        self.SubPathIndex = Uint8()


class IdtHznEdge(SomeIpPayload):

    IdtHznEdge: IdtHznEdgeKls

    def __init__(self):

        self.IdtHznEdge = IdtHznEdgeKls()
