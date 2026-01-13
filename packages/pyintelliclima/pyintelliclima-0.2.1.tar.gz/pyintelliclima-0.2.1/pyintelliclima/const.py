from enum import StrEnum

# API endpoints
API_BASE_URL = "https://intelliclima.fantinicosmi.it"
API_MONO = "/server_v1_mono/api/"


class FanSpeed(StrEnum):
    """Fan speed options for EcoComfort VMC devices."""

    off = "0"
    sleep = "1"
    low = "2"
    medium = "3"
    high = "4"
    auto = "16"


class FanMode(StrEnum):
    """Fan mode/direction options for EcoComfort VMC devices."""

    off = "0"
    inward = "1"
    outward = "2"
    alternate = "3"
    sensor = "4"
