"""
Support for KWB Easyfire.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.kwb/
"""
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_HOST, CONF_PORT,
    CONF_NAME)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['pykwb==0.0.1']

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 23
DEFAULT_TYPE = 'tcp'

MODE_SERIAL = 0
MODE_TCP = 1


SERIAL_SCHEMA = {
    vol.Required(CONF_PORT): cv.string,
    vol.Required(CONF_TYPE): 'serial',
}

ETHERNET_SCHEMA = {
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): cv.positive_int,
    vol.Required(CONF_TYPE): 'tcp',
}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the KWB component."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    type = config.get(CONF_type)

    from pykwb import KWBEasyfire
    
    if (type == 'serial'):
        kwb = KWBEasyfire(MODE_SERIAL, "", 0, port)
    elif (type == 'tcp'):
        kwb = KWBEasyfire(MODE_TCP, host, port)
    else:
        return False
    
    for sensor in kwb.get_sensors():
        add_devices(KWBSensor(kwb, sensor))


class KWBSensor(Entity):
    """Representation of a KWB Easyfire sensor."""

    def __init__(self, kwb, sensor):
        """Initialize the KWB sensor."""
        
        from pykwb import KWBEasyfireSensor
        
        self._kwb = kwb
        self._sensor = sensor

    @property
    def name(self):
        """Return the name."""
        return self._sensor.name

    @property
    def should_poll(self):  # pylint: disable=no-self-use
        """No polling needed."""
        return False

    # pylint: disable=no-member
    @property
    def state(self):
        """Return the state of value."""
        return self._sensor.value

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._sensor.unit_of_measurement

