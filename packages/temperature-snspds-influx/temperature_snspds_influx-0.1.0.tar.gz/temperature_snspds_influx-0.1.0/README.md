# Temperature SNSPDs influx

This script is used to monitor the temperature of a SNSPDs system ([IDQ 281 SNSPD system](https://www.idquantique.com/quantum-detection-systems/products/id281-snspd-system/) in this case), running with the [SRS CTC100 Temperature controller](https://www.thinksrs.com/products/ctc100.html). In particular, the scripts periodically retrieves the temperature value from the CTC (using USB or Ethernet interface) and write the values to an [Influx](https://github.com/influxdata/influxdb) time series database.

Outside of this script, the data is visualized using [Grafana](https://grafana.com/).

## Installing the package

The software can be installed from [Pypi](https://pypi.org/project/temperature-snspds-influx/) using the following command:

```bash
pip install temperature-snspds-influx
```

or 

```bash
python -m pip install temperature-snspds-influx
```

You can check that the package has been succesfully installed by executing the command:

```bash
temperature-snspds-influx --version
```

or 

```bash
python -m temperature_snspds_influx --version
```

The command help can be retrieved with `-h` or `--help`.

## Configuration

The example configuration file can be copied to the current directory in the `config.toml` file by simply running the `temperature-snspds-influx` script (with no file located at the target file). The target file can be changed with the `-f` or `--file` command line parameter.

All the parameters of the configuration file must be set.

The example configuration file is displayed below and can be found [here](temperature_snspds_influx/config.example.toml):

```toml
# Configuration file for temperature-snspds-influx.

[influx]

# Endpoint of the influx database.
endpoint = ""

# Token to use for influxdb.
token = ""

# Name of the database to write to.
db = ""

[ctc]

# Method to connect to the CTC. It should be either "usb" or "ethernet".
method = ""

# Address of the CTC. It should be a COM port or tty for USB
# and ip_address:port for ethernet.
address = ""

# Name of the instrument that recovers the data.
instrument = ""

# Number of digits requested to the CTC (1, 2, 3, 4, 5 or 6).
precision = 6
```

## Running the script

The script can be executed with the following command:

```bash
temperature-snspds-influx -f config.toml -l temperature-snspds-influx.log -vvv
```

where the `-f config.toml` is to make it explicit in this example, the `-l temperature-snspds-influx.log` to set a log file and `-vvv` to specify a log level.

## License

This software is released under the MIT license. For more details, check the LICENSE file or visit [https://opensource.org/licenses/MIT](https://opensource.org/licenses/MIT).