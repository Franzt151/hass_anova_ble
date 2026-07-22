"""Constants for anova_bluetooth."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Anova Bluetooth"
DOMAIN = "anova_bluetooth"

# Keep in sync with the "version" field in manifest.json.
VERSION = "0.1.2"

# Shown in the device card. This is the hardware, not a version number.
MODEL = "Precision Cooker (Bluetooth)"
