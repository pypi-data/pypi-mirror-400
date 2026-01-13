from someip_py.codec import *


class IdtExceptionuniquesourceidStruct(SomeIpPayload):

    _include_struct_len = True

    Installationorder: SomeIpDynamicSizeString

    Clientversion: SomeIpDynamicSizeString

    def __init__(self):

        self.Installationorder = SomeIpDynamicSizeString()

        self.Clientversion = SomeIpDynamicSizeString()


class IdtExceptionmessageStruct(SomeIpPayload):

    _include_struct_len = True

    Activity: SomeIpDynamicSizeString

    Action: SomeIpDynamicSizeString

    Exception: SomeIpDynamicSizeString

    LogParams: SomeIpDynamicSizeString

    def __init__(self):

        self.Activity = SomeIpDynamicSizeString()

        self.Action = SomeIpDynamicSizeString()

        self.Exception = SomeIpDynamicSizeString()

        self.LogParams = SomeIpDynamicSizeString()


class IdtExceptionreportsStruct(SomeIpPayload):

    _include_struct_len = True

    ExceptionuniquesourceidStruct: IdtExceptionuniquesourceidStruct

    Isotimestamp: SomeIpDynamicSizeString

    Issuerid: SomeIpDynamicSizeString

    FileName: SomeIpDynamicSizeString

    EcuAddress: SomeIpDynamicSizeString

    KeyName: SomeIpDynamicSizeString

    DataBlock: SomeIpDynamicSizeString

    ExceptionmessageStruct: IdtExceptionmessageStruct

    def __init__(self):

        self.ExceptionuniquesourceidStruct = IdtExceptionuniquesourceidStruct()

        self.Isotimestamp = SomeIpDynamicSizeString()

        self.Issuerid = SomeIpDynamicSizeString()

        self.FileName = SomeIpDynamicSizeString()

        self.EcuAddress = SomeIpDynamicSizeString()

        self.KeyName = SomeIpDynamicSizeString()

        self.DataBlock = SomeIpDynamicSizeString()

        self.ExceptionmessageStruct = IdtExceptionmessageStruct()


class IdtInstallStatusStructKls(SomeIpPayload):

    _include_struct_len = True

    Exceptionreportmsgremaining: Int16

    ExceptionreportsStruct: IdtExceptionreportsStruct

    def __init__(self):

        self.Exceptionreportmsgremaining = Int16()

        self.ExceptionreportsStruct = IdtExceptionreportsStruct()


class IdtInstallStatusStruct(SomeIpPayload):

    IdtInstallStatusStruct: IdtInstallStatusStructKls

    def __init__(self):

        self.IdtInstallStatusStruct = IdtInstallStatusStructKls()
