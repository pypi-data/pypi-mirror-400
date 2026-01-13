from someip_py.codec import *


class IdtADAlertAlarmAttribute(SomeIpPayload):

    Key: Uint8

    Value: Int16

    def __init__(self):

        self.Key = Uint8()

        self.Value = Int16()


class IdtADAlertAlarmInfoInfStsKls(SomeIpPayload):
    _has_dynamic_size = True

    AlarmID: Uint32

    AlarmAttributes: SomeIpDynamicSizeArray[IdtADAlertAlarmAttribute]

    def __init__(self):

        self.AlarmID = Uint32()

        self.AlarmAttributes = SomeIpDynamicSizeArray(IdtADAlertAlarmAttribute)


class IdtADAlertAlarmInfoInfSts(SomeIpPayload):

    IdtADAlertAlarmInfoInfSts: IdtADAlertAlarmInfoInfStsKls

    def __init__(self):

        self.IdtADAlertAlarmInfoInfSts = IdtADAlertAlarmInfoInfStsKls()
