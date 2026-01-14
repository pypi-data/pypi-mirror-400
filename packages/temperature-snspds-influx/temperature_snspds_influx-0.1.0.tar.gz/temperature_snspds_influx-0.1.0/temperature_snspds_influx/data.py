# Copyright (c) 2026 Yoann Piétri
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

"""
Data container, reader and publisher.
"""

import datetime
from dataclasses import dataclass

from influxdb_client_3 import InfluxDBClient3, Point

from temperature_snspds_influx.ctc import CTC100


@dataclass
class Data:
    """
    A data point containing the datetime and temperatures (Tr, Tp, Tsw, T1s) and voltage (switch, hpump) of the CTC.
    """

    time: datetime.datetime
    tr: float
    tp: float
    tsw: float
    t1s: float
    switch: float
    hpump: float


def get_data(
    ctc: CTC100,
) -> Data:
    """Get a data point from the CTC.

    Args:
        ctc (CTC100): the ctc object to get the data from.

    Returns:
        Data: the data point.
    """
    return Data(
        datetime.datetime.now(),
        ctc.get_channel("Tr"),
        ctc.get_channel("Tp"),
        ctc.get_channel("Tsw"),
        ctc.get_channel("T1s"),
        ctc.get_channel("Switch"),
        ctc.get_channel("Hpump"),
    )


def publish_data(data: Data, instrument: str, client: InfluxDBClient3) -> None:
    """Publish the data point using the influxdb3 client.

    Args:
        data (Data): data to publish.
        instrument (str): instrument used to acquire the date (set as a tag).
        client (InfluxDBClient3): influxdb3 client to publish the data.
    """
    point = (
        Point("ctc100")
        .tag("instrument", instrument)
        .field("Tr", data.tr)
        .field("Tp", data.tp)
        .field("Tsw", data.tsw)
        .field("T1s", data.t1s)
        .field("Switch", data.switch)
        .field("Hpump", data.hpump)
        .time(data.time)
    )
    client.write(point)
