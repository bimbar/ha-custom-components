"""
Support for eq3 Bluetooth Smart thermostats.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/thermostat.max/
"""
import logging

from homeassistant.components.thermostat import ThermostatDevice
from homeassistant.const import TEMP_CELCIUS
from homeassistant.helpers.temperature import convert

import struct
from bluepy import btle
import binascii
from datetime import datetime

REQUIREMENTS = []

CONF_MAC = 'mac'
CONF_DEVICES = 'devices'
CONF_ID = 'id'

PROPERTY_WRITE_HANDLE=0x411
PROPERTY_NTFY_HANDLE=0x421
PROPERTY_ID_VALUE=struct.pack('B', 0)
PROPERTY_GETINFO_VALUE=struct.pack('B', 3)
PROPERTY_TEMPERATURE_VALUE_RAW=0x41
PROPERTY_TEMPERATURE_VALUE=struct.pack('B', PROPERTY_TEMPERATURE_VALUE_RAW)


_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the eq3 BLE thermostats."""
    devices = []

    for name, device_cfg in config[CONF_DEVICES].items():
        mac = device_cfg[CONF_MAC]
        devices.append(eq3BTSmartThermostat(mac, name))

    add_devices(devices)
    return True


# pylint: disable=too-many-instance-attributes
class eq3BTSmartThermostat(ThermostatDevice, btle.DefaultDelegate):
    """Representation of a Homematic thermostat."""

    def __init__(self, _mac, _name):
        """Initialize the thermostat."""
        btle.DefaultDelegate.__init__(self)

        self._mac = _mac
        self._name = _name
        self._target_temperature = -1
        self._mode = -1
        self._requestValue = -1
        self._requestHandle = -1
        
        self._conn = btle.Peripheral()
        self._connect()
        self.update()


    def _connect(self):
        _LOGGER.info("EQ3 Smart BLE: connecting to " + self._name + " " + self._mac)
        self._conn.connect(self._mac)
        self._conn.withDelegate(self)
        self._setTime()
    
    def _setTime(self):
        """Set the correct time into the thermostat"""
        time=datetime.now()
        value=struct.pack('BBBBBB', int(time.strftime("%y")), time.month, time.day, time.hour, time.minute, time.second)
        self.writeCommandRaw(PROPERTY_WRITE_HANDLE, value)
        

    def _disconnect(self):
        self._conn.disconnect()

    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        return True

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement that is used."""
        return TEMP_CELCIUS


    @property
    def current_temperature(self):
        """This thermostat can not report the current temperature (at least at the moment), so return the target temperature."""
        return self.target_temperature
                        

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    def set_temperature(self, temperature):
        """Set new target temperature."""
        value=struct.pack('BB', PROPERTY_TEMPERATURE_VALUE_RAW, int(temperature*2))
        self.writeRequestRaw(PROPERTY_WRITE_HANDLE, value) 
        self._target_temperature=temperature

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {"mode": self._mode}

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return round(convert(4.5, TEMP_CELCIUS, self.unit_of_measurement))

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return round(convert(30.5, TEMP_CELCIUS, self.unit_of_measurement))

    def decodeMode(self, mode):
        ret = ""
        if (mode&1):
            ret = "manual"
        else:
            ret = "auto"
        
        if (mode&2):
            ret = ret + " holiday"
        if (mode&4):
            ret = ret + " boost"
        if (mode&8):
            ret = ret + " dst"
        if (mode&16):
            ret = ret + " window"
        
        return ret
        

    def handleNotification(self, cHandle, data):
        if (cHandle == PROPERTY_NTFY_HANDLE):
            if (self._requestValue == PROPERTY_GETINFO_VALUE):
                self._mode=self.decodeMode(data[2])
                self._target_temperature=data[5]/2.0

    
    def writeRequest(self, handle, value):
        self.writeCommand(handle, value, True)

    def writeRequestRaw(self, handle, value):
        self.writeCommandRaw(handle, value, True)

    def writeCommand(self, handle, value, waitForIt=False):
        self.writeCommand(handle, value.encode('utf-8'), waitForIt)
    
    def writeCommandRaw(self, handle, value, waitForIt=False, exception=False):
        try:
            self._requestHandle = handle
            self._requestValue = value
            self._conn.writeCharacteristic(handle, value, waitForIt)
            if (waitForIt):
                while self._conn.waitForNotifications(0.1):
                    continue
        except btle.BTLEException:
            if (exception==False):
                self._disconnect()
                self._connect()
                self.writeCommandRaw(handle, value, waitForIt, True)

        

    def update(self, exception=False):
        """Update the data from the thermostat."""
        self.writeRequestRaw(PROPERTY_WRITE_HANDLE, PROPERTY_GETINFO_VALUE)



#thermostat = eq3BTSmartThermostat('00:1A:22:07:85:31', 'buero')
#thermostat.update()
#thermostat.set_temperature(22.5)
