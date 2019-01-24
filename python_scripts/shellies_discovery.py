"""
Adds MQTT discovery support for Shellies.
Arguments:
 - discovery_prefix:    - discovery prefix in HA, default 'homeassistant',
                          optional
 - id       			- Shellie ID (required)
 - mac                  - Shellie MAC address (required)
 - sensor				- sensor entity_id (required)
 - fw_ver               - Shellie firmware version (optional)
 - list of shelies relays and components for them

Configuration example:
Automations:
- id: shellies_announce
  alias: 'Shellies Announce'
  trigger:
    - platform: homeassistant
      event: start
  action:
    service: mqtt.publish
    data:
      topic: shellies/command
      payload: announce

- id: 'shellies_discovery'
  alias: 'Shellies Discovery'
  trigger:
  - platform: mqtt
    topic: shellies/announce
  action:
    service: python_script.shellies_discovery
    data_template:
      discovery_prefix: 'hass'
      id: '{{ trigger.payload_json.id }}'
      mac: '{{ trigger.payload_json.mac }}'
      fw_ver: '{{ trigger.payload_json.fw_ver }}'
      shelly1-328900-relay-0: 'light'
      shellyswitch-5B2604-relay-0: 'switch'
      shellyswitch-5B2604-relay-1: 'light'

Argument 'shellyswitch-5B2604-relay-1: light' means that relay 1 of
shellyswitch-5B2604 will be the light in Home Assistant. You can use switch,
light or fan.

Script supports custom_updater component. Add this to your configuration and
stay up-to-date.

custom_updater:
  track:
    - python_scripts
  python_script_urls:
    - https://raw.githubusercontent.com/bieniu/home-assistant-config/master/python_scripts/python_scripts.json
"""

VERSION = '0.0.1'

ATTR_ID = 'id'
ATTR_MAC = 'mac'
ATTR_FW_VER = 'fw_ver'
ATTR_DISCOVERY_PREFIX = 'discovery_prefix'

id = data.get(ATTR_ID)
mac = data.get(ATTR_MAC)
fw_ver = data.get(ATTR_FW_VER)
disc_prefix = 'homeassistant'
if data.get(ATTR_DISCOVERY_PREFIX) is not None:
    disc_prefix = data.get(ATTR_DISCOVERY_PREFIX)

if id is None or mac is None:
    logger.error("Expected id and mac as arguments.")
else:
    relays = 0
    relay_sensors = []
    relay_components = ['switch', 'light', 'fan']

    if 'shellyswitch' in id:
        model = 'Shelly2'
        component = 'switch'
        relays = 2
        relay_sensors = ['power']
        units = ['W']
        templates = ['{{ value | round }}']

    if 'shelly1' in id:
        model = 'Shelly1'
        component = 'switch'
        relays = 1

    for i in range(0, relays):
        device_name = '{} {}'.format(model, id.split('-')[1],)
        relay_name = '{} Relay {}'.format(device_name, i)
        default_topic = 'shellies/{}/'.format(id)
        state_topic = '~relay/{}'.format(i)
        command_topic =  '{}/command'.format(state_topic)
        availability_topic = '~online'
        unique_id = '{}-relay-{}'.format(id, i)
        if data.get(unique_id):
            component = data.get(unique_id)
            if component in relay_components:
                config_topic = '{}/{}/{}-relay-{}/config'.format(disc_prefix,
                                                              component, id, i)
                payload = '{\"name\":\"' + relay_name + '\",' \
                          '\"cmd_t\":\"' + command_topic + '\",' \
                          '\"stat_t\":\"' + state_topic +'\",' \
                          '\"pl_off\":\"off\",' \
                          '\"pl_on\":\"on\",' \
                          '\"avty_t\":\"' + availability_topic + '\",' \
                          '\"pl_avail\":\"true\",' \
                          '\"pl_not_avail\":\"false\",' \
                          '\"uniq_id\":\"' + unique_id + '\",' \
                          '\"device\": {\"identifiers\": [\"' + mac + '\"],' \
                          '\"name\":\"' + device_name + '\",' \
                          '\"model\":\"' + model + '\",' \
                          '\"sw_version\":\"' + fw_ver + '\",' \
                          '\"manufacturer\":\"Shelly\"},' \
                          '\"~\":\"' + default_topic + '\"}'
                service_data = {
                    'topic': config_topic,
                    'payload': payload,
                    'retain': True,
                    'qos': 0
                }
                hass.services.call('mqtt', 'publish', service_data, False)
        if i == relays-1:
            for l in range(0, len(relay_sensors)):
                unique_id = '{}-relay-{}'.format(id, relay_sensors[l])
                config_topic = '{}/sensor/{}-{}/config'.format(disc_prefix, id,
                                                              relay_sensors[l])
                sensor_name = '{} {}'.format(device_name,
                                             relay_sensors[l].capitalize())
                state_topic =  '~relay/{}'.format(relay_sensors[l])
                payload = '{\"name\":\"' + sensor_name + '\",' \
                          '\"stat_t\":\"' + state_topic + '\",' \
                          '\"unit_of_meas\":\"' + units[l] + '\",' \
                          '\"val_tpl\":\"' + templates[l] + '\",' \
                          '\"avty_t\":\"' + availability_topic + '\",' \
                          '\"pl_avail\":\"true\",' \
                          '\"pl_not_avail\":\"false\",' \
                          '\"uniq_id\":\"' + unique_id + '\",' \
                          '\"device\": {\"identifiers\": [\"' + mac + '\"],' \
                          '\"name\":\"' + device_name + '\",' \
                          '\"model\":\"' + model + '\",' \
                          '\"sw_version\":\"' + fw_ver + '\",' \
                          '\"manufacturer\":\"Shelly\"},' \
                          '\"~\":\"' + default_topic + '\"}'
                service_data = {
                    'topic': config_topic,
                    'payload': payload,
                    'retain': True,
                    'qos': 0
                }
                hass.services.call('mqtt', 'publish', service_data, False)
