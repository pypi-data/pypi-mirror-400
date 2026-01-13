from someip_py.codec import *


class IdtCameraparameterreqstructKls(SomeIpPayload):

    Frontcamerarequest: Uint8

    Rearcamerarequest: Uint8

    Leftcamerarequest: Uint8

    Rightcamerarequest: Uint8

    def __init__(self):

        self.Frontcamerarequest = Uint8()

        self.Rearcamerarequest = Uint8()

        self.Leftcamerarequest = Uint8()

        self.Rightcamerarequest = Uint8()


class IdtCameraparameterreqstruct(SomeIpPayload):

    IdtCameraparameterreqstruct: IdtCameraparameterreqstructKls

    def __init__(self):

        self.IdtCameraparameterreqstruct = IdtCameraparameterreqstructKls()
