from someip_py.codec import *


class IdtDHUToADCUDTCStructKls(SomeIpPayload):

    Frontcamera_Circuitshorttoground: Uint8

    Frontcamera_Circuitopen: Uint8

    Frontcamera_signalinvalid: Uint8

    Frontcamera_Overtemperature: Uint8

    Frontcamera_retry: Uint8

    Rearcamera_Circuitshorttoground: Uint8

    Rearcamera_Circuitopen: Uint8

    Rearcamera_signalinvalid: Uint8

    Rearcamera_Overtemperature: Uint8

    Rearcamera_retry: Uint8

    Leftcamera_Circuitshorttoground: Uint8

    Leftcamera_Circuitopen: Uint8

    Leftcamera_signalinvalid: Uint8

    Leftcamera_Overtemperature: Uint8

    Leftcamera_retry: Uint8

    Rightcamera_Circuitshorttoground: Uint8

    Rightcamera_Circuitopen: Uint8

    Rightcamera_signalinvalid: Uint8

    Rightcamera_Overtemperature: Uint8

    Rightcamera_retry: Uint8

    def __init__(self):

        self.Frontcamera_Circuitshorttoground = Uint8()

        self.Frontcamera_Circuitopen = Uint8()

        self.Frontcamera_signalinvalid = Uint8()

        self.Frontcamera_Overtemperature = Uint8()

        self.Frontcamera_retry = Uint8()

        self.Rearcamera_Circuitshorttoground = Uint8()

        self.Rearcamera_Circuitopen = Uint8()

        self.Rearcamera_signalinvalid = Uint8()

        self.Rearcamera_Overtemperature = Uint8()

        self.Rearcamera_retry = Uint8()

        self.Leftcamera_Circuitshorttoground = Uint8()

        self.Leftcamera_Circuitopen = Uint8()

        self.Leftcamera_signalinvalid = Uint8()

        self.Leftcamera_Overtemperature = Uint8()

        self.Leftcamera_retry = Uint8()

        self.Rightcamera_Circuitshorttoground = Uint8()

        self.Rightcamera_Circuitopen = Uint8()

        self.Rightcamera_signalinvalid = Uint8()

        self.Rightcamera_Overtemperature = Uint8()

        self.Rightcamera_retry = Uint8()


class IdtDHUToADCUDTCStruct(SomeIpPayload):

    IdtDHUToADCUDTCStruct: IdtDHUToADCUDTCStructKls

    def __init__(self):

        self.IdtDHUToADCUDTCStruct = IdtDHUToADCUDTCStructKls()
