from someip_py.codec import *


class IdtAmbienceIntensityFb(SomeIpPayload):

    Zone: Uint8

    CurrentIntensity: Uint8

    DayIntensity: Uint8

    NightIntensity: Uint8

    def __init__(self):

        self.Zone = Uint8()

        self.CurrentIntensity = Uint8()

        self.DayIntensity = Uint8()

        self.NightIntensity = Uint8()


class IdtAmbienceIntensityFbAry(SomeIpPayload):

    IdtAmbienceIntensityFb: SomeIpDynamicSizeArray[IdtAmbienceIntensityFb]

    def __init__(self):

        self.IdtAmbienceIntensityFb = SomeIpDynamicSizeArray(IdtAmbienceIntensityFb)
