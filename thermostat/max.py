"""
Support for Max!Cube thermostats.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/thermostat.max/

configuration.yaml

thermostat:
  platform: max
  ip: <IP of MaxCube>
  port: <Port of MaxCube - default is 62910>
"""
import logging

from homeassistant.components.thermostat import ThermostatDevice
from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.temperature import convert

from maxcube.connection import *
from maxcube.cube import *
from maxcube.device import *
from maxcube.thermostat import *


REQUIREMENTS = ['python-maxcube-api']

CONF_IP = 'ip'
CONF_PORT = 'port'
PROPERTY_SET_TEMPERATURE = 'SET_TEMPERATURE'
PROPERTY_ACTUAL_TEMPERATURE = 'ACTUAL_TEMPERATURE'
PROPERTY_MODE = 'MODE'

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Max!Cube thermostat."""
    devices = []
    try:
        cubeConn = MaxCubeConnection(config[CONF_IP], config[CONF_PORT])
        cube = MaxCube(cubeConn)
        for device in cube.get_devices():
            devices.append(MaxThermostat(cube, device.rf_address))
    except socket.error:
        _LOGGER.exception("Connection error to Max!Cube")
        return False

    add_devices(devices)
    return True


# pylint: disable=too-many-instance-attributes
class MaxThermostat(ThermostatDevice):
    """Representation of a Homematic thermostat."""

    def __init__(self, cube, _id):
        """Initialize the thermostat."""
        self.cube = cube
        self._id = _id
        self._device = cube.device_by_rf(_id)

    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        return True


    @property
    def name(self):
        """Return the name of the Homematic device."""
        return self._device.name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement that is used."""
        return TEMP_CELCIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._device.actual_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._device.target_temperature

    def set_temperature(self, temperature):
        """Set new target temperature."""
        self.cube.set_target_temperature(self._device, temperature)

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {"mode": self._device.mode}

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return round(convert(4.5, TEMP_CELCIUS, self.unit_of_measurement))

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return round(convert(30.5, TEMP_CELCIUS, self.unit_of_measurement))


    def update(self):
        """Update the data from the thermostat."""
        try:
            self.cube.update()
        except socket.error:
            _LOGGER.exception("Did not receive any temperature data from the "
                              "Max!Cube API.")
