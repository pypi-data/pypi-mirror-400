from someip_py.codec import *


class IdtDHUtoADCUParaMeterStruct(SomeIpPayload):

    Camera_DateTime_yy: Uint8

    Camera_DateTime_MM: Uint8

    Camera_DateTime_dd: Uint8

    Camera_MAP_VER_NUMBER: Uint8

    Camera_DIST_MODEL: Uint8

    Camera_Fx: Float64

    Camera_Fy: Float64

    Camera_Cx: Float64

    Camera_Cy: Float64

    Camera_k1: Float64

    Camera_k2: Float64

    Camera_k3: Float64

    Camera_k4: Float64

    Camera_k5: Float64

    Camera_k6: Float64

    P1: Float64

    P2: Float64

    P3: Float64

    P4: Float64

    SN: SomeIpFixedSizeArray[Uint8]

    AVERAGE_DEVIATION: Float64

    MAX_ERROR: Float64

    Camera_CRC_Flag: Uint8

    CRC32: Uint32

    def __init__(self):

        self.Camera_DateTime_yy = Uint8()

        self.Camera_DateTime_MM = Uint8()

        self.Camera_DateTime_dd = Uint8()

        self.Camera_MAP_VER_NUMBER = Uint8()

        self.Camera_DIST_MODEL = Uint8()

        self.Camera_Fx = Float64()

        self.Camera_Fy = Float64()

        self.Camera_Cx = Float64()

        self.Camera_Cy = Float64()

        self.Camera_k1 = Float64()

        self.Camera_k2 = Float64()

        self.Camera_k3 = Float64()

        self.Camera_k4 = Float64()

        self.Camera_k5 = Float64()

        self.Camera_k6 = Float64()

        self.P1 = Float64()

        self.P2 = Float64()

        self.P3 = Float64()

        self.P4 = Float64()

        self.SN = SomeIpFixedSizeArray(Uint8, size=32)

        self.AVERAGE_DEVIATION = Float64()

        self.MAX_ERROR = Float64()

        self.Camera_CRC_Flag = Uint8()

        self.CRC32 = Uint32()


class IdtDHUtoADCUParaMeterArray(SomeIpPayload):

    DHUtoADCUParaMeterStruct: SomeIpDynamicSizeArray[IdtDHUtoADCUParaMeterStruct]

    def __init__(self):

        self.DHUtoADCUParaMeterStruct = SomeIpDynamicSizeArray(
            IdtDHUtoADCUParaMeterStruct
        )
