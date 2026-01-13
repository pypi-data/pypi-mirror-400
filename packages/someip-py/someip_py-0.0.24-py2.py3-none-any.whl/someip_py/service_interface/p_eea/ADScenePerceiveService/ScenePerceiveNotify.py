from someip_py.codec import *


class IdtScenePerceiveStsKls(SomeIpPayload):

    SceneEnterExit: Uint8

    SceneType: Uint8

    PositionInfo: Uint16

    DistanceInfo: Uint32

    ReservedPara: SomeIpFixedSizeArray[Uint16]

    def __init__(self):

        self.SceneEnterExit = Uint8()

        self.SceneType = Uint8()

        self.PositionInfo = Uint16()

        self.DistanceInfo = Uint32()

        self.ReservedPara = SomeIpFixedSizeArray(Uint16, size=20)


class IdtScenePerceiveSts(SomeIpPayload):

    IdtScenePerceiveSts: IdtScenePerceiveStsKls

    def __init__(self):

        self.IdtScenePerceiveSts = IdtScenePerceiveStsKls()
