from someip_py.codec import *


class IdtAmbMusicDataArray(SomeIpPayload):

    IdtMusicShowData: SomeIpFixedSizeArray[Uint8]

    def __init__(self):

        self.IdtMusicShowData = SomeIpFixedSizeArray(Uint8, size=12)


class IdtAmbienceAppReturnCode(SomeIpPayload):

    IdtAmbienceAppReturnCode: Uint8

    def __init__(self):

        self.IdtAmbienceAppReturnCode = Uint8()
