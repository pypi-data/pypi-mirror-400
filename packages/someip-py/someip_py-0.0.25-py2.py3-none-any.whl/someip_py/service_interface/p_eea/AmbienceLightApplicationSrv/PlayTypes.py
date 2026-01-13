from someip_py.codec import *


class IdtMusicShowPlayType(SomeIpPayload):

    IdtMusicShowPlayType: Uint8

    def __init__(self):

        self.IdtMusicShowPlayType = Uint8()


class IdtAmbienceAppReturnCode(SomeIpPayload):

    IdtAmbienceAppReturnCode: Uint8

    def __init__(self):

        self.IdtAmbienceAppReturnCode = Uint8()
