VERSION = "0.2.0"

PROTOCOL_VERSION = 1
FEATURE_LEVEL = 3

FEATURE_OTA_FW_UPDATE = 2
FEATURE_IDENTIFY = 3


def supports(dev, feat):
    return dev.get("feature_level", 0) >= feat
