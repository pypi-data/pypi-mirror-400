from someip_py.codec import *


class IdtAmbienceFuncSettingSlice(SomeIpPayload):

    Zone: Uint8

    FunctionSwitch: Uint8

    def __init__(self):

        self.Zone = Uint8()

        self.FunctionSwitch = Uint8()


class IdtAmbFuncSwtSet(SomeIpPayload):

    IdtAmbienceFuncSettingSlice: SomeIpDynamicSizeArray[IdtAmbienceFuncSettingSlice]

    def __init__(self):

        self.IdtAmbienceFuncSettingSlice = SomeIpDynamicSizeArray(
            IdtAmbienceFuncSettingSlice
        )


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
