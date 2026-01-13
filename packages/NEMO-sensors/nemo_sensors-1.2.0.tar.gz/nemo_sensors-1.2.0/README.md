# NEMO Sensors

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/NEMO-sensors?label=python)](https://www.python.org/downloads/release/python-3110/)
[![PyPI](https://img.shields.io/pypi/v/nemo-sensors?label=pypi%20version)](https://pypi.org/project/NEMO-sensors/)
[![Changelog](https://img.shields.io/github/v/tag/usnistgov/NEMO-sensors?include_prereleases&label=changelog)](https://github.com/usnistgov/NEMO-sensors/tags)

Plugin for NEMO allowing to connect to sensors to collect data and set alerts.

## Installation

```bash
python -m install nemo-sensors
```

in `settings.py` add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    '...',
    'NEMO_sensors',
    # 'NEMO.apps.sensors' Remove old dependency
    '...'
]
```

To enabled sensor data pulling, set a cron job running every minute with one of the following options:

1. send an authenticated http request to `<nemo_url>/manage_sensor_data/`
2. run command `django-admin manage_sensor_data` or `python manage.py manage_sensor_data`

Example of `systemd` service and timer files are provided for your convenience in the [systemd folder](https://github.com/usnistgov/NEMO-sensors/tree/master/resources/systemd).


## Usage

Usage instructions go here.

# Tests

To run the tests:
```bash
python runtests.py
```
