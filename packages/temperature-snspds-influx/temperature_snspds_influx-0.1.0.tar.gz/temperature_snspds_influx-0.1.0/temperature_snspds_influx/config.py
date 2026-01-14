# Copyright (c) 2026 Yoann Piétri
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Config reader for temperature-snspds-influx.
"""

from typing import Dict
import logging
import tomllib

logger = logging.getLogger(__name__)


# pylint: disable=too-few-public-methods
class AutoConfiguration:
    """A class to automatically fill a configuration class from a dict read from the toml file."""

    def __init__(self, config_dict: Dict):
        self._from_dict(config_dict)

    def _from_dict(self, config_dict: Dict):
        """Assign the values from the dictionnary.

        Args:
            config_dict (Dict): dictionnary read from the toml file.
        """
        for key, val in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, val)
            else:
                logger.warning("Got an unexpected configuration paramater: %s", key)


class CTCConfiguration(AutoConfiguration):
    """Configuration for the CTC."""

    method: str = ""  #: Method to connect to the CTC (usb or ethernet).
    address: str = ""  #: Address to connect to (COM port or tty or ip_address:port).
    instrument: str = ""  #: Name of the instrument for tagging the measurement.
    precision: int = 6  #: Number of digits required.


class InfluxConfiguration(AutoConfiguration):
    """Configuration for the influx database."""

    endpoint: str = ""  #: Endpoint of the influx database.
    token: str = ""  #: Token to interact with influx.
    db: str = ""  #: Database to write points to.


class Configuration:
    """Overall configuration for temperature-snspds-influx."""

    ctc: CTCConfiguration  #: Configuration object of the CTC.
    influx: InfluxConfiguration  #: Configuration object of the influx db.

    def __init__(self, config_path: str):
        """
        Args:
            config_path (str): path of the configuration file.

        Raises:
            ValueError: if the ctc section is absent from the configuration file.
            ValueError: if the influx section is absent from the configuration file.
        """
        with open(config_path, "rb") as fp:
            config = tomllib.load(fp)

        if "ctc" not in config:
            raise ValueError("ctc is not present in configuration file.")

        if "influx" not in config:
            raise ValueError("influx is not present in configuration file.")

        self.ctc = CTCConfiguration(config["ctc"])
        self.influx = InfluxConfiguration(config["influx"])
