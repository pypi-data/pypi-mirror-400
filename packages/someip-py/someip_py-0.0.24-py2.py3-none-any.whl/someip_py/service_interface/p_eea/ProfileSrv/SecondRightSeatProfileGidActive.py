from someip_py.codec import *


class IdtProfileInformationKls(SomeIpPayload):

    ProfileGidValue: SomeIpDynamicSizeString

    GIDType: Uint8

    def __init__(self):

        self.ProfileGidValue = SomeIpDynamicSizeString()

        self.GIDType = Uint8()


class IdtProfileInformation(SomeIpPayload):

    IdtProfileInformation: IdtProfileInformationKls

    def __init__(self):

        self.IdtProfileInformation = IdtProfileInformationKls()
