from someip_py.codec import *


class IdtFIVEGModeStructKls(SomeIpPayload):

    _include_struct_len = True

    FIVEGMode: Uint8

    RtnVal: Uint8

    def __init__(self):

        self.FIVEGMode = Uint8()

        self.RtnVal = Uint8()


class IdtFIVEGModeStruct(SomeIpPayload):

    IdtFIVEGModeStruct: IdtFIVEGModeStructKls

    def __init__(self):

        self.IdtFIVEGModeStruct = IdtFIVEGModeStructKls()
