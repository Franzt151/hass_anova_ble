"""Constants for anova_bluetooth."""
from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

NAME = "Anova Bluetooth"
DOMAIN = "anova_bluetooth"

# NOTE: the integration version is read at runtime from manifest.json
# (see __init__.py); it is deliberately not duplicated here.

# Shown in the device card. This is the hardware, not a version number.
MODEL = "Precision Cooker (Bluetooth)"
