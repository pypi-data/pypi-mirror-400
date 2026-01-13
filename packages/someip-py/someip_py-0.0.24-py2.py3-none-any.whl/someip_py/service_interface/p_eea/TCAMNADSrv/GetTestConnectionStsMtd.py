from someip_py.codec import *


class IdtTcamDtcInfo(SomeIpPayload):

    DtcCode: SomeIpDynamicSizeString

    DtcCodeValue: SomeIpDynamicSizeString

    def __init__(self):

        self.DtcCode = SomeIpDynamicSizeString()

        self.DtcCodeValue = SomeIpDynamicSizeString()


class IdtTcamDtcTestStatus(SomeIpPayload):
    _has_dynamic_size = True

    TcamDtcStatus: Bool

    TcamDtcList: SomeIpDynamicSizeArray[IdtTcamDtcInfo]

    def __init__(self):

        self.TcamDtcStatus = Bool()

        self.TcamDtcList = SomeIpDynamicSizeArray(IdtTcamDtcInfo)


class IdtSimIMSIInfo(SomeIpPayload):

    SimNo: Uint8

    SimIMSIInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimIMSIInfo = SomeIpDynamicSizeString()


class IdtSimICCIDInfo(SomeIpPayload):

    SimNo: Uint8

    SimICCIDInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimICCIDInfo = SomeIpDynamicSizeString()


class IdtSimMSISDNInfo(SomeIpPayload):

    SimNo: Uint8

    SimMSISDNInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimMSISDNInfo = SomeIpDynamicSizeString()


class IdtSimIMEIInfo(SomeIpPayload):

    SimNo: Uint8

    SimIMEIInfo: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimIMEIInfo = SomeIpDynamicSizeString()


class IdtSimCardInfo(SomeIpPayload):
    _has_dynamic_size = True

    SimIMSI: SomeIpDynamicSizeArray[IdtSimIMSIInfo]

    SimICCID: SomeIpDynamicSizeArray[IdtSimICCIDInfo]

    SimMSISDN: SomeIpDynamicSizeArray[IdtSimMSISDNInfo]

    SimIMEI: SomeIpDynamicSizeArray[IdtSimIMEIInfo]

    def __init__(self):

        self.SimIMSI = SomeIpDynamicSizeArray(IdtSimIMSIInfo)

        self.SimICCID = SomeIpDynamicSizeArray(IdtSimICCIDInfo)

        self.SimMSISDN = SomeIpDynamicSizeArray(IdtSimMSISDNInfo)

        self.SimIMEI = SomeIpDynamicSizeArray(IdtSimIMEIInfo)


class IdtSimTestStatus(SomeIpPayload):
    _has_dynamic_size = True

    SimStatus: Bool

    SimCardInfo: IdtSimCardInfo

    def __init__(self):

        self.SimStatus = Bool()

        self.SimCardInfo = IdtSimCardInfo()


class IdtConnectInfoList(SomeIpPayload):

    ConnUrl: SomeIpDynamicSizeString

    Responsetime: Uint16

    ConnStatus: Bool

    Packetloss: Uint8

    def __init__(self):

        self.ConnUrl = SomeIpDynamicSizeString()

        self.Responsetime = Uint16()

        self.ConnStatus = Bool()

        self.Packetloss = Uint8()


class IdtConnectTestStatus(SomeIpPayload):

    ConnectStatus: Uint8

    ConnectInfoList: IdtConnectInfoList

    def __init__(self):

        self.ConnectStatus = Uint8()

        self.ConnectInfoList = IdtConnectInfoList()


class IdtSimCnctnSts(SomeIpPayload):

    SimNo: Uint8

    SimCnctnSts: Uint8

    def __init__(self):

        self.SimNo = Uint8()

        self.SimCnctnSts = Uint8()


class IdtSimOperatorSts(SomeIpPayload):

    SimNo: Uint8

    SimOperatorSts: Uint8

    def __init__(self):

        self.SimNo = Uint8()

        self.SimOperatorSts = Uint8()


class IdtSimIPAdr(SomeIpPayload):

    SimNo: Uint8

    SimIPAdr: SomeIpDynamicSizeString

    def __init__(self):

        self.SimNo = Uint8()

        self.SimIPAdr = SomeIpDynamicSizeString()


class IdtRSRPInfo(SomeIpPayload):

    SimNo: Uint8

    RSRP: Int16

    def __init__(self):

        self.SimNo = Uint8()

        self.RSRP = Int16()


class IdtNetworkinfo(SomeIpPayload):
    _has_dynamic_size = True

    SimConStatus: IdtSimCnctnSts

    SimOperatorStatus: IdtSimOperatorSts

    LteMode: Uint8

    SimCardInfo: IdtSimCardInfo

    Ipadr: IdtSimIPAdr

    Rssnr: Uint8

    Rsrq: Uint8

    Rsrp: IdtRSRPInfo

    Rssi: Uint8

    Mcc: SomeIpDynamicSizeString

    Mnc: SomeIpDynamicSizeString

    Earfcn: Uint16

    Lac: Uint16

    Tac: Uint32

    Pci: Uint16

    def __init__(self):

        self.SimConStatus = IdtSimCnctnSts()

        self.SimOperatorStatus = IdtSimOperatorSts()

        self.LteMode = Uint8()

        self.SimCardInfo = IdtSimCardInfo()

        self.Ipadr = IdtSimIPAdr()

        self.Rssnr = Uint8()

        self.Rsrq = Uint8()

        self.Rsrp = IdtRSRPInfo()

        self.Rssi = Uint8()

        self.Mcc = SomeIpDynamicSizeString()

        self.Mnc = SomeIpDynamicSizeString()

        self.Earfcn = Uint16()

        self.Lac = Uint16()

        self.Tac = Uint32()

        self.Pci = Uint16()


class IdtNetworkTestStatus(SomeIpPayload):
    _has_dynamic_size = True

    NetworkStatus: Bool

    Networkinfo: IdtNetworkinfo

    def __init__(self):

        self.NetworkStatus = Bool()

        self.Networkinfo = IdtNetworkinfo()


class IdtSmsTestStatus(SomeIpPayload):
    _has_dynamic_size = True

    SimStatus: Bool

    SimCardInfo: IdtSimCardInfo

    def __init__(self):

        self.SimStatus = Bool()

        self.SimCardInfo = IdtSimCardInfo()


class IdtGpsInfo(SomeIpPayload):

    Longitude: Int32

    Latitude: Int32

    def __init__(self):

        self.Longitude = Int32()

        self.Latitude = Int32()


class IdtTestConnectionStsKls(SomeIpPayload):
    _has_dynamic_size = True

    VIN: SomeIpDynamicSizeString

    TemID: SomeIpDynamicSizeString

    TcamDtcTestStatus: IdtTcamDtcTestStatus

    SimTestStatus: IdtSimTestStatus

    ConnectTestStatus: IdtConnectTestStatus

    NetworkTestStatus: IdtNetworkTestStatus

    SmsTestStatus: IdtSmsTestStatus

    GpsInfo: IdtGpsInfo

    CallTestStatus: Bool

    Gnssfault: Uint8

    Wififault: Uint8

    Modemfault: Uint8

    Mcufault: Uint8

    Cpuusagerate: Uint8

    Emmcfreespace: Uint32

    Memoryfreespace: Uint32

    RtnVal: Uint8

    def __init__(self):

        self.VIN = SomeIpDynamicSizeString()

        self.TemID = SomeIpDynamicSizeString()

        self.TcamDtcTestStatus = IdtTcamDtcTestStatus()

        self.SimTestStatus = IdtSimTestStatus()

        self.ConnectTestStatus = IdtConnectTestStatus()

        self.NetworkTestStatus = IdtNetworkTestStatus()

        self.SmsTestStatus = IdtSmsTestStatus()

        self.GpsInfo = IdtGpsInfo()

        self.CallTestStatus = Bool()

        self.Gnssfault = Uint8()

        self.Wififault = Uint8()

        self.Modemfault = Uint8()

        self.Mcufault = Uint8()

        self.Cpuusagerate = Uint8()

        self.Emmcfreespace = Uint32()

        self.Memoryfreespace = Uint32()

        self.RtnVal = Uint8()


class IdtTestConnectionSts(SomeIpPayload):

    IdtTestConnectionSts: IdtTestConnectionStsKls

    def __init__(self):

        self.IdtTestConnectionSts = IdtTestConnectionStsKls()
