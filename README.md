# ha-custom-components

Custom Components for homeassistant (http://www.home-assistant.io) which I am too lazy to try to integrate into upstream at the moment.

Copy into ha_config_dir/custom-components/

Configuration:

MAX:

thermostat:
  platform: max
  ip: IP
  port: PORT

eq3btsmart:

thermostat:
  platform: eq3btsmart
  devices:
    NAME:
      mac: 00:11:22:33:44:55
