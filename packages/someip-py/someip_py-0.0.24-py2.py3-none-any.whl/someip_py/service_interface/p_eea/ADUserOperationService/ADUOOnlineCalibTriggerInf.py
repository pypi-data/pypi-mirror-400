from someip_py.codec import *


class IdtADUOOnlineCalibTriggerKls(SomeIpPayload):

    OnlineCalibTrigger: Uint8

    CalibItems: Uint32

    def __init__(self):

        self.OnlineCalibTrigger = Uint8()

        self.CalibItems = Uint32()


class IdtADUOOnlineCalibTrigger(SomeIpPayload):

    IdtADUOOnlineCalibTrigger: IdtADUOOnlineCalibTriggerKls

    def __init__(self):

        self.IdtADUOOnlineCalibTrigger = IdtADUOOnlineCalibTriggerKls()


class IdtADUORet(SomeIpPayload):

    IdtADUORet: Uint8

    def __init__(self):

        self.IdtADUORet = Uint8()
