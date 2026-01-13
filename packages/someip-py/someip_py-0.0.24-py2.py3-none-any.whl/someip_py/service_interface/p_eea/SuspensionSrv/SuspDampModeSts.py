from someip_py.codec import *


class IdtDampModeSts(SomeIpPayload):

    IdtDampModeSts: Uint8

    def __init__(self):

        self.IdtDampModeSts = Uint8()
