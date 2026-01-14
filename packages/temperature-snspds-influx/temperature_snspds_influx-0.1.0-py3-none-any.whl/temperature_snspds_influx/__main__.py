# Copyright (c) 2026 Yoann Piétri
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Main entrypoint for temperature-snspds-influx.
"""

import sys
import time
import shutil
import logging
import argparse
from pathlib import Path
from typing import Tuple, Optional, Type

from influxdb_client_3 import InfluxDBClient3

from temperature_snspds_influx import __version__
from temperature_snspds_influx.config import Configuration
from temperature_snspds_influx.data import Data, get_data, publish_data
from temperature_snspds_influx.ctc import EthernetCTC100, USBCTC100, CTC100

logger = logging.getLogger(__name__)

DEFAULT_REFRESH_TIME = 60  #: Default refresh time in seconds.


def _create_parser() -> argparse.ArgumentParser:
    """Create the parser for the command.

    Returns:
        argparse.ArgumentParser: parser for the command.
    """
    parser = argparse.ArgumentParser("temperature-snspds-influx")

    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Level of verbosity. If none, only critical errors will be prompted. -v will add warnings and errors, -vv will add info and -vvv will print all debug logs.",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="config.toml",
        help="Path of the file to create. Default : config.toml.",
    )
    parser.add_argument(
        "-r",
        "--refresh",
        type=float,
        default=DEFAULT_REFRESH_TIME,
        help=f"Refresh time in seconds. Default: {DEFAULT_REFRESH_TIME}.",
    )
    parser.add_argument("-l", "--log-path", help="Log path for the log file.")
    return parser


def _verbose_to_log_level(verbose: int) -> int:
    """Return the log level (as int), depending on
    the verbosity level (corresponding to the numbers of -v
    given in parameter).

    0 -v : Only display critical logs.
    1 -v : Display critical, error and warning logs.
    2 -v : Display critical, error, warning and info logs.
    3 or more -v : Display every log.

    Args:
        verbose (int): the verbosity level.

    Returns:
        int: the log level.
    """
    if verbose == 0:
        return logging.CRITICAL

    if verbose == 1:
        return logging.WARNING

    if verbose == 2:
        return logging.INFO

    return logging.DEBUG


def _create_loggers(
    verbose: int, log_path: str | None
) -> Tuple[logging.Logger, logging.Handler, Optional[logging.Handler]]:
    """Create the loggers.

    Args:
        verbose (int): the verbose level, as an integer.
        log_path (str | None): the path of the log file or None if no file logging is wanted.

    Returns:
        Tuple[logging.Logger, logging.Handler, Optional[logging.Handler]]: the root logger, the console handler and the optional file handler.
    """
    log_level = _verbose_to_log_level(verbose)

    root_logger = logging.getLogger("")
    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    if log_path:
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    else:
        file_handler = None

    return root_logger, console_handler, file_handler


def _create_influx_client(
    config: Configuration, old_client: InfluxDBClient3 | None = None
) -> InfluxDBClient3:
    """Create the influx client, closing the old one if it exists.

    Args:
        config (Configuration): the configuration object to configure the client.
        old_client (InfluxDBClient3 | None, optional): the old client or None. Defaults to None.

    Returns:
        InfluxDBClient3: the influxdb3 client.
    """
    if old_client is not None:
        try:
            old_client.close()
        except Exception as exc:
            logger.error(exc)

    logger.info("Creating client.")
    return InfluxDBClient3(
        host=config.influx.endpoint,
        token=config.influx.token,
        database=config.influx.db,
    )


def _create_ctc(config: Configuration, old_ctc: CTC100 | None = None) -> CTC100:
    """Create the CTC object, closing the old one if it exists.

    Args:
        config (Configuration): the configuration object to configure the CTC.
        old_ctc (CTC100 | None, optional): the old CTC or None. Defaults to None.

    Raises:
        ValueError: if the method is neither usb or ethernet. The comparaison is case insensitive.

    Returns:
        CTC100: the CTC object.
    """
    if old_ctc is not None:
        try:
            old_ctc.close()
        except Exception as exc:
            logger.error(exc)
    cls: Type[CTC100]
    if config.ctc.method.lower() == "usb":
        cls = USBCTC100
    elif config.ctc.method.lower() == "ethernet":
        cls = EthernetCTC100
    else:
        raise ValueError(f"Unknown method for CTC: {config.ctc.method}")
    logger.info("Creating CTC.")
    return cls(config.ctc.address, config.ctc.precision)


def main() -> None:
    """Main entrypoint for temperature-snspds-influx."""
    parser = _create_parser()
    args = parser.parse_args()

    _create_loggers(args.verbose, args.log_path)

    if not Path(args.file).exists():
        print("args.file does not exists. Copy default configuration to this location.")
        shutil.copy(Path(__file__).parent / "config.example.toml", args.file)
        print(f"Default configuration file was copied to {args.file}.")
        sys.exit(0)

    config = Configuration(args.file)

    client = _create_influx_client(config)
    ctc = _create_ctc(config)

    data: Data | None

    try:
        while True:
            try:
                ctc.open()
                data = get_data(ctc)
                ctc.close()
                logger.info(data)
            except Exception as exc:
                logger.error(exc)
                data = None
                ctc = _create_ctc(config, ctc)
            if data is not None:
                try:
                    publish_data(data, config.ctc.instrument, client)
                except Exception as exc:
                    logger.error(exc)
                    client = _create_influx_client(config, client)
            time.sleep(args.refresh)
    except KeyboardInterrupt:
        logger.warning("Interruption received")
    finally:
        ctc.close()
        client.close()


if __name__ == "__main__":
    main()
