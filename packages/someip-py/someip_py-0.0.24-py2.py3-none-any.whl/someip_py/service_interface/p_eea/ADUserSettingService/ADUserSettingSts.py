from someip_py.codec import *


class IdtADUSItem(SomeIpPayload):

    Key: Uint16

    Value: Int16

    def __init__(self):

        self.Key = Uint16()

        self.Value = Int16()


class IdtADUSItems(SomeIpPayload):

    IdtADUSItem: SomeIpDynamicSizeArray[IdtADUSItem]

    def __init__(self):

        self.IdtADUSItem = SomeIpDynamicSizeArray(IdtADUSItem)
