from someip_py.codec import *


class IdtAmbienceIntensity(SomeIpPayload):

    Zone: Uint8

    Intensity: Uint8

    def __init__(self):

        self.Zone = Uint8()

        self.Intensity = Uint8()


class IdtAmbienceIntensityAry(SomeIpPayload):

    IdtAmbienceIntensity: SomeIpDynamicSizeArray[IdtAmbienceIntensity]

    def __init__(self):

        self.IdtAmbienceIntensity = SomeIpDynamicSizeArray(IdtAmbienceIntensity)


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
