from someip_py.codec import *


class IdtAmbienceInhibitSrc(SomeIpPayload):

    IdtAmbienceInhibitSrc: Uint8

    def __init__(self):

        self.IdtAmbienceInhibitSrc = Uint8()


class IdtAmbienceInhibitType(SomeIpPayload):

    IdtAmbienceInhibitType: Uint8

    def __init__(self):

        self.IdtAmbienceInhibitType = Uint8()


class IdtAppReturnCode(SomeIpPayload):

    IdtAppReturnCode: Uint8

    def __init__(self):

        self.IdtAppReturnCode = Uint8()
