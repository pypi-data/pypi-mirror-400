from someip_py.codec import *


class IdtHznDataKls(SomeIpPayload):

    CountryCode: Uint16

    CyclicCounter: Uint8

    DrivingSide: Uint8

    HardwareVersion: Uint16

    MajorProtocolVersion: Uint8

    MapProvider: Uint8

    MessageType: Uint8

    RegionCode: Uint16

    MapVersionYear: Uint8

    MapVersionYearQuarter: Uint8

    MinorProtocolSubVersion: Uint8

    MinorProtocolVersion: Uint8

    SpeedUnits: Uint8

    def __init__(self):

        self.CountryCode = Uint16()

        self.CyclicCounter = Uint8()

        self.DrivingSide = Uint8()

        self.HardwareVersion = Uint16()

        self.MajorProtocolVersion = Uint8()

        self.MapProvider = Uint8()

        self.MessageType = Uint8()

        self.RegionCode = Uint16()

        self.MapVersionYear = Uint8()

        self.MapVersionYearQuarter = Uint8()

        self.MinorProtocolSubVersion = Uint8()

        self.MinorProtocolVersion = Uint8()

        self.SpeedUnits = Uint8()


class IdtHznData(SomeIpPayload):

    IdtHznData: IdtHznDataKls

    def __init__(self):

        self.IdtHznData = IdtHznDataKls()
