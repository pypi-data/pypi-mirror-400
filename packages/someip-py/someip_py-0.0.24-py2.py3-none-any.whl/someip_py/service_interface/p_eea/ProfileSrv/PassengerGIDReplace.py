from someip_py.codec import *


class IdtGIDReplaceKls(SomeIpPayload):

    OldGid: SomeIpDynamicSizeString

    NewGid: SomeIpDynamicSizeString

    def __init__(self):

        self.OldGid = SomeIpDynamicSizeString()

        self.NewGid = SomeIpDynamicSizeString()


class IdtGIDReplace(SomeIpPayload):

    IdtGIDReplace: IdtGIDReplaceKls

    def __init__(self):

        self.IdtGIDReplace = IdtGIDReplaceKls()
