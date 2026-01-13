from someip_py.codec import *


class IdtMusicShowSetSwt(SomeIpPayload):

    IdtMusicShowSetSwt: Uint8

    def __init__(self):

        self.IdtMusicShowSetSwt = Uint8()
