from someip_py.codec import *


class IdtSimCnctnSts(SomeIpPayload):

    SimNo: Uint8

    SimCnctnSts: Uint8

    def __init__(self):

        self.SimNo = Uint8()

        self.SimCnctnSts = Uint8()


class IdtSimHiSpdFun(SomeIpPayload):

    SimHiSpdFun: Bool

    SimNo: Uint8

    def __init__(self):

        self.SimHiSpdFun = Bool()

        self.SimNo = Uint8()


class IdtSimNetAvl(SomeIpPayload):

    SimNo: Uint8

    SimNetAvl: Bool

    def __init__(self):

        self.SimNo = Uint8()

        self.SimNetAvl = Bool()


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


class IdtSimSigStrength(SomeIpPayload):

    SimNo: Uint8

    SimSigStrength: Uint8

    def __init__(self):

        self.SimNo = Uint8()

        self.SimSigStrength = Uint8()


class IdtSimSigLevel(SomeIpPayload):

    SimNo: Uint8

    SimSigLevel: Uint8

    def __init__(self):

        self.SimNo = Uint8()

        self.SimSigLevel = Uint8()


class IdtSimDataCnctnSts(SomeIpPayload):

    SimNo: Uint8

    SimDataCnctnSts: Uint8

    def __init__(self):

        self.SimNo = Uint8()

        self.SimDataCnctnSts = Uint8()


class IdtSimTrfcData(SomeIpPayload):

    SimNo: Uint8

    SimTxbytecount: Uint64

    SimRxbytecount: Uint64

    def __init__(self):

        self.SimNo = Uint8()

        self.SimTxbytecount = Uint64()

        self.SimRxbytecount = Uint64()


class IdtTrafficDataStruct(SomeIpPayload):
    _has_dynamic_size = True

    TrafficData1: SomeIpDynamicSizeArray[IdtSimTrfcData]

    TrafficData2: SomeIpDynamicSizeArray[IdtSimTrfcData]

    TrafficData3: SomeIpDynamicSizeArray[IdtSimTrfcData]

    def __init__(self):

        self.TrafficData1 = SomeIpDynamicSizeArray(IdtSimTrfcData)

        self.TrafficData2 = SomeIpDynamicSizeArray(IdtSimTrfcData)

        self.TrafficData3 = SomeIpDynamicSizeArray(IdtSimTrfcData)


class IdtSimNetSpeed(SomeIpPayload):

    IdtSimNo: Uint8

    IdtTxbytecount: Uint64

    IdtRxbytecount: Uint64

    def __init__(self):

        self.IdtSimNo = Uint8()

        self.IdtTxbytecount = Uint64()

        self.IdtRxbytecount = Uint64()


class IdtNetWorkSpeedInfo(SomeIpPayload):
    _has_dynamic_size = True

    NetSpeedForAPN1: SomeIpDynamicSizeArray[IdtSimNetSpeed]

    NetSpeedForAPN2: SomeIpDynamicSizeArray[IdtSimNetSpeed]

    NetSpeedForAPN3: SomeIpDynamicSizeArray[IdtSimNetSpeed]

    def __init__(self):

        self.NetSpeedForAPN1 = SomeIpDynamicSizeArray(IdtSimNetSpeed)

        self.NetSpeedForAPN2 = SomeIpDynamicSizeArray(IdtSimNetSpeed)

        self.NetSpeedForAPN3 = SomeIpDynamicSizeArray(IdtSimNetSpeed)


class IdtESIMstatusKls(SomeIpPayload):
    _has_dynamic_size = True

    ESIMConnectionStatus: SomeIpDynamicSizeArray[IdtSimCnctnSts]

    Hispeedfun: SomeIpDynamicSizeArray[IdtSimHiSpdFun]

    NetworkAvailable: SomeIpDynamicSizeArray[IdtSimNetAvl]

    OperatorStatus: SomeIpDynamicSizeArray[IdtSimOperatorSts]

    IPAddress: SomeIpDynamicSizeArray[IdtSimIPAdr]

    SignalStrength: SomeIpDynamicSizeArray[IdtSimSigStrength]

    SignalLevel: SomeIpDynamicSizeArray[IdtSimSigLevel]

    DataConnectionStatus: SomeIpDynamicSizeArray[IdtSimDataCnctnSts]

    RSRPInfo: SomeIpDynamicSizeArray[Int16]

    BLERInfo: SomeIpDynamicSizeArray[Uint8]

    SINRInfo: SomeIpDynamicSizeArray[Int16]

    TrafficDataStruct: IdtTrafficDataStruct

    NetWorkSpeedInfo: IdtNetWorkSpeedInfo

    def __init__(self):

        self.ESIMConnectionStatus = SomeIpDynamicSizeArray(IdtSimCnctnSts)

        self.Hispeedfun = SomeIpDynamicSizeArray(IdtSimHiSpdFun)

        self.NetworkAvailable = SomeIpDynamicSizeArray(IdtSimNetAvl)

        self.OperatorStatus = SomeIpDynamicSizeArray(IdtSimOperatorSts)

        self.IPAddress = SomeIpDynamicSizeArray(IdtSimIPAdr)

        self.SignalStrength = SomeIpDynamicSizeArray(IdtSimSigStrength)

        self.SignalLevel = SomeIpDynamicSizeArray(IdtSimSigLevel)

        self.DataConnectionStatus = SomeIpDynamicSizeArray(IdtSimDataCnctnSts)

        self.RSRPInfo = SomeIpDynamicSizeArray(Int16)

        self.BLERInfo = SomeIpDynamicSizeArray(Uint8)

        self.SINRInfo = SomeIpDynamicSizeArray(Int16)

        self.TrafficDataStruct = IdtTrafficDataStruct()

        self.NetWorkSpeedInfo = IdtNetWorkSpeedInfo()


class IdtESIMstatus(SomeIpPayload):

    IdtESIMstatus: IdtESIMstatusKls

    def __init__(self):

        self.IdtESIMstatus = IdtESIMstatusKls()
