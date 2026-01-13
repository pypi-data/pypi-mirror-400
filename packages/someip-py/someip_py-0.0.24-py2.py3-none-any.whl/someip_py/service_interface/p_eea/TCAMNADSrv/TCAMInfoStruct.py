from someip_py.codec import *


class IdtTCAMInfoStructKls(SomeIpPayload):

    DU: SomeIpDynamicSizeString

    SWBL: SomeIpDynamicSizeString

    SWLM_MCU: SomeIpDynamicSizeString

    SWLM_SOC: SomeIpDynamicSizeString

    SWP1: SomeIpDynamicSizeString

    SWLX_BLE: SomeIpDynamicSizeString

    SWLX_SE: SomeIpDynamicSizeString

    SWLX_WPC: SomeIpDynamicSizeString

    SWLX_NKRSE: SomeIpDynamicSizeString

    SWLX_NKR: SomeIpDynamicSizeString

    SWLX_DKAM: SomeIpDynamicSizeString

    SWLX_STCM: SomeIpDynamicSizeString

    ID: SomeIpDynamicSizeString

    SWLX_DKAM_MCU: SomeIpDynamicSizeString

    SWLX_DKAM_BLE: SomeIpDynamicSizeString

    SWLX_DKAM_UWB: SomeIpDynamicSizeString

    HWSDHWKN: SomeIpDynamicSizeString

    SXBL: SomeIpDynamicSizeString

    SXDISXBL: SomeIpDynamicSizeString

    def __init__(self):

        self.DU = SomeIpDynamicSizeString()

        self.SWBL = SomeIpDynamicSizeString()

        self.SWLM_MCU = SomeIpDynamicSizeString()

        self.SWLM_SOC = SomeIpDynamicSizeString()

        self.SWP1 = SomeIpDynamicSizeString()

        self.SWLX_BLE = SomeIpDynamicSizeString()

        self.SWLX_SE = SomeIpDynamicSizeString()

        self.SWLX_WPC = SomeIpDynamicSizeString()

        self.SWLX_NKRSE = SomeIpDynamicSizeString()

        self.SWLX_NKR = SomeIpDynamicSizeString()

        self.SWLX_DKAM = SomeIpDynamicSizeString()

        self.SWLX_STCM = SomeIpDynamicSizeString()

        self.ID = SomeIpDynamicSizeString()

        self.SWLX_DKAM_MCU = SomeIpDynamicSizeString()

        self.SWLX_DKAM_BLE = SomeIpDynamicSizeString()

        self.SWLX_DKAM_UWB = SomeIpDynamicSizeString()

        self.HWSDHWKN = SomeIpDynamicSizeString()

        self.SXBL = SomeIpDynamicSizeString()

        self.SXDISXBL = SomeIpDynamicSizeString()


class IdtTCAMInfoStruct(SomeIpPayload):

    IdtTCAMInfoStruct: IdtTCAMInfoStructKls

    def __init__(self):

        self.IdtTCAMInfoStruct = IdtTCAMInfoStructKls()
