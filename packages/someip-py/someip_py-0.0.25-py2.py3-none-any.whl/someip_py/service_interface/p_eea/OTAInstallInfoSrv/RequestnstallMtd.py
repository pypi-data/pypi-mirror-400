from someip_py.codec import *


class IdtRequestnstall(SomeIpPayload):

    IdtRequestnstall: SomeIpDynamicSizeString

    def __init__(self):

        self.IdtRequestnstall = SomeIpDynamicSizeString()


class IdtRequestnstallRespStructKls(SomeIpPayload):

    _include_struct_len = True

    Status: SomeIpDynamicSizeString

    RetVal: Uint8

    def __init__(self):

        self.Status = SomeIpDynamicSizeString()

        self.RetVal = Uint8()


class IdtRequestnstallRespStruct(SomeIpPayload):

    IdtRequestnstallRespStruct: IdtRequestnstallRespStructKls

    def __init__(self):

        self.IdtRequestnstallRespStruct = IdtRequestnstallRespStructKls()
