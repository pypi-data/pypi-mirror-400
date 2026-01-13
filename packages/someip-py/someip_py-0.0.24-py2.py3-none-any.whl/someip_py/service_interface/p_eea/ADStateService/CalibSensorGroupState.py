from someip_py.codec import *


class IdtCalibSensorGroupStateKls(SomeIpPayload):

    AllSensorCalibState: Uint8

    SensorCalibGroup: Uint8

    OnlineCalibProgress: Uint8

    def __init__(self):

        self.AllSensorCalibState = Uint8()

        self.SensorCalibGroup = Uint8()

        self.OnlineCalibProgress = Uint8()


class IdtCalibSensorGroupState(SomeIpPayload):

    IdtCalibSensorGroupState: IdtCalibSensorGroupStateKls

    def __init__(self):

        self.IdtCalibSensorGroupState = IdtCalibSensorGroupStateKls()
