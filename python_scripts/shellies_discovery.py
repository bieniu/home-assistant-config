"""
This script adds MQTT discovery support for Shellies. Shelly1, Shelly2,
Shelly4Pro, Shelly Plug and Shelly Plug are supported.
Arguments:
 - discovery_prefix:    - discovery prefix in HA, default 'homeassistant',
                          optional
 - id       			- Shelly ID (required)
 - mac                  - Shelly MAC address (required)
 - sensor				- sensor entity_id (required)
 - fw_ver               - Shelly firmware version (optional)
 - temp_unit            - C for Celsius, F for Farenhait, default C (optional)
 - list of shelies relays and components for them, only for devices with relays
                          (optional), by default all relays are added as
                          switches.

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
      temp_unit: 'F'
      shelly1-328900-relay-0: 'light'
      shellyswitch-5B2604-relay-0: 'switch'
      shellyswitch-5B2604-relay-1: 'light'
      shelly4pro-122656-relay-0: 'switch'
      shelly4pro-122656-relay-1: 'fan'
      shelly4pro-122656-relay-2: 'switch'
      shelly4pro-122656-relay-3: 'switch'
      shellyswitch-5B1200-roller-0: 'cover'

Argument 'shellyswitch-5B2604-relay-1: light' means that relay 1 of
shellyswitch-5B2604 will be the light in Home Assistant. You can use switch,
light or fan.
Argument shellyswitch-5B1200-roller-0: 'cover' means that Shelly2 works in
roller mode and use cover component in Home Assistant.

Script supports custom_updater component. Add this to your configuration and
stay up-to-date.

custom_updater:
  track:
    - python_scripts
  python_script_urls:
    - https://raw.githubusercontent.com/bieniu/home-assistant-config/master/python_scripts/python_scripts.json
"""

VERSION = '0.4.1'

ATTR_DEVELOP = 'develop'

ATTR_ID = 'id'
ATTR_MAC = 'mac'
ATTR_FW_VER = 'fw_ver'
ATTR_DISCOVERY_PREFIX = 'discovery_prefix'
ATTR_TEMP_UNIT = 'temp_unit'

develop = False
retain = True
roller_mode = False

id = data.get(ATTR_ID)
mac = data.get(ATTR_MAC)
fw_ver = data.get(ATTR_FW_VER)
temp_unit = '°C'
if data.get(ATTR_TEMP_UNIT) is not None:
    if data.get(ATTR_TEMP_UNIT) == 'F':
        temp_unit = '°F'
disc_prefix = 'homeassistant'
if data.get(ATTR_DISCOVERY_PREFIX) is not None:
    disc_prefix = data.get(ATTR_DISCOVERY_PREFIX)

if data.get(ATTR_DEVELOP) is not None:
    develop = data.get(ATTR_DEVELOP)
if develop:
    disc_prefix = 'develop'
    retain = False
    logger.error("DEVELOP MODE !!!")

if id is None or mac is None:
    logger.error("Expected id and mac as arguments.")
else:
    relays = 0
    rollers = 0
    relay_sensors = []
    relay_components = ['switch', 'light', 'fan']
    sensors = []
    config_component = 'switch'

    if 'shelly1' in id:
        model = 'Shelly1'
        relays = 1

    if 'shellyswitch' in id:
        model = 'Shelly2'
        relays = 2
        rollers = 1
        relay_sensors = ['power']
        units = ['W']
        templates = ['{{ value | round(1) }}']        

    if 'shellyplug' in id:
        model = 'Shelly Plug'
        relays = 1
        relay_sensors = ['power', 'energy']
        units = ['W', 'kWh']
        templates = ['{{ value | round(1) }}',
                     '{{ (value | float / 100) | round(2) }}']

    if 'shelly4pro' in id:
        model = 'Shelly4Pro'
        relays = 4
        relay_sensors = ['power', 'energy']
        units = ['W', 'kWh']
        templates = ['{{ value | round(1) }}',
                     '{{ (value / 100) | round(2) }}']

    if 'shellyht' in id:
        model = 'ShellyH&T'
        sensors = ['temperature', 'humidity', 'battery']
        units = [temp_unit, '%', '%']
        templates = ['{{ value | round(1) }}',
                     '{{ value | round(1) }}',
                     '{{ value | round }}']
                     
    for roller_id in range(0, rollers):
        device_name = '{} {}'.format(model, id.split('-')[1],)
        roller_name = '{} Roller {}'.format(device_name, roller_id)
        default_topic = 'shellies/{}/'.format(id)
        state_topic = '{}roller/{}'.format(default_topic, roller_id)
        command_topic =  '{}/command'.format(state_topic)
        position_topic =  '{}/pos'.format(state_topic)
        set_position_topic =  '{}/command/pos'.format(state_topic)
        availability_topic = '{}online'.format(default_topic)
        unique_id = '{}-roller-{}'.format(id, roller_id)
        if data.get(unique_id):
            config_component = data.get(unique_id)
        component = 'cover'      
        config_topic = '{}/{}/{}-roller-{}/config'.format(disc_prefix,
                                                    component, id, roller_id)
        if config_component == component:
            roller_mode = True
            payload = '{\"name\":\"' + roller_name + '\",' \
                      '\"command_topic\":\"' + command_topic + '\",' \
                      '\"position_topic\":\"' + position_topic + '\",' \
                      '\"set_position_topic\":\"' + set_position_topic + '\",' \
                      '\"payload_open\":\"open\",' \
                      '\"payload_close\":\"close\",' \
                      '\"payload_stop\":\"stop\",' \
                      '\"optimistic\":\"false\",' \
                      '\"availability_topic\":\"' + availability_topic + '\",' \
                      '\"payload_available\":\"true\",' \
                      '\"payload_not_available\":\"false\",' \
                      '\"unique_id\":\"' + unique_id + '\",' \
                      '\"device\": {\"ids\": [\"' + mac + '\"],' \
                      '\"name\":\"' + device_name + '\",' \
                      '\"model\":\"' + model + '\",' \
                      '\"sw_version\":\"' + fw_ver + '\",' \
                      '\"manufacturer\":\"Shelly\"},' \
                      '\"~\":\"' + default_topic + '\"}'
        else:
            payload = ''    
        service_data = {
                'topic': config_topic,
                'payload': payload,
                'retain': retain,
                'qos': 0
            }            
        hass.services.call('mqtt', 'publish', service_data, False)

    for relay_id in range(0, relays):
        device_name = '{} {}'.format(model, id.split('-')[1],)
        relay_name = '{} Relay {}'.format(device_name, relay_id)
        default_topic = 'shellies/{}/'.format(id)
        state_topic = '~relay/{}'.format(relay_id)
        command_topic =  '{}/command'.format(state_topic)
        availability_topic = '~online'
        unique_id = '{}-relay-{}'.format(id, relay_id)
        if data.get(unique_id):
            config_component = data.get(unique_id)
        for component in relay_components:
            config_topic = '{}/{}/{}-relay-{}/config'.format(disc_prefix,
                                                    component, id, relay_id)
            if component == config_component and not roller_mode:
                payload = '{\"name\":\"' + relay_name + '\",' \
                          '\"cmd_t\":\"' + command_topic + '\",' \
                          '\"stat_t\":\"' + state_topic +'\",' \
                          '\"pl_off\":\"off\",' \
                          '\"pl_on\":\"on\",' \
                          '\"avty_t\":\"' + availability_topic + '\",' \
                          '\"pl_avail\":\"true\",' \
                          '\"pl_not_avail\":\"false\",' \
                          '\"uniq_id\":\"' + unique_id + '\",' \
                          '\"dev\": {\"ids\": [\"' + mac + '\"],' \
                          '\"name\":\"' + device_name + '\",' \
                          '\"mdl\":\"' + model + '\",' \
                          '\"sw\":\"' + fw_ver + '\",' \
                          '\"mf\":\"Shelly\"},' \
                          '\"~\":\"' + default_topic + '\"}'
            else:
                payload = ''
            service_data = {
                'topic': config_topic,
                'payload': payload,
                'retain': retain,
                'qos': 0
            }            
            hass.services.call('mqtt', 'publish', service_data, False)

        if model == 'Shelly2':
            if relay_id == relays-1:
                for sensor_id in range(0, len(relay_sensors)):
                    unique_id = '{}-relay-{}'.format(id,
                                                     relay_sensors[sensor_id])
                    config_topic = '{}/sensor/{}-{}/config'.format(disc_prefix,
                                                  id, relay_sensors[sensor_id])
                    sensor_name = '{} {}'.format(device_name,
                                         relay_sensors[sensor_id].capitalize())
                    state_topic =  '~relay/{}'.format(relay_sensors[sensor_id])
                    payload = '{\"name\":\"' + sensor_name + '\",' \
                              '\"stat_t\":\"' + state_topic + '\",' \
                              '\"unit_of_meas\":\"' + units[sensor_id] + '\",' \
                              '\"val_tpl\":\"' + templates[sensor_id] + '\",' \
                              '\"avty_t\":\"' + availability_topic + '\",' \
                              '\"pl_avail\":\"true\",' \
                              '\"pl_not_avail\":\"false\",' \
                              '\"uniq_id\":\"' + unique_id + '\",' \
                              '\"dev\": {\"ids\": [\"' + mac + '\"],' \
                              '\"name\":\"' + device_name + '\",' \
                              '\"mdl\":\"' + model + '\",' \
                              '\"sw\":\"' + fw_ver + '\",' \
                              '\"mf\":\"Shelly\"},' \
                              '\"~\":\"' + default_topic + '\"}'
                    service_data = {
                        'topic': config_topic,
                        'payload': payload,
                        'retain': retain,
                        'qos': 0
                    }
                    hass.services.call('mqtt', 'publish', service_data, False)
        else:
            for sensor_id in range(0, len(relay_sensors)):
                unique_id = '{}-relay-{}-{}'.format(id,
                                            relay_sensors[sensor_id], relay_id)
                config_topic = '{}/sensor/{}-{}-{}/config'.format(disc_prefix,
                                        id, relay_sensors[sensor_id], relay_id)
                sensor_name = '{} {} {}'.format(device_name,
                               relay_sensors[sensor_id].capitalize(), relay_id)
                state_topic =  '~relay/{}/{}'.format(relay_id,
                                                      relay_sensors[sensor_id])
                payload = '{\"name\":\"' + sensor_name + '\",' \
                          '\"stat_t\":\"' + state_topic + '\",' \
                          '\"unit_of_meas\":\"' + units[sensor_id] + '\",' \
                          '\"val_tpl\":\"' + templates[sensor_id] + '\",' \
                          '\"avty_t\":\"' + availability_topic + '\",' \
                          '\"pl_avail\":\"true\",' \
                          '\"pl_not_avail\":\"false\",' \
                          '\"uniq_id\":\"' + unique_id + '\",' \
                          '\"dev\": {\"ids\": [\"' + mac + '\"],' \
                          '\"name\":\"' + device_name + '\",' \
                          '\"mdl\":\"' + model + '\",' \
                          '\"sw\":\"' + fw_ver + '\",' \
                          '\"mf\":\"Shelly\"},' \
                          '\"~\":\"' + default_topic + '\"}'
                service_data = {
                    'topic': config_topic,
                    'payload': payload,
                    'retain': retain,
                    'qos': 0
                }
                hass.services.call('mqtt', 'publish', service_data, False)

    for sensor_id in range(0, len(sensors)):
        device_name = '{} {}'.format(model, id.split('-')[1],)
        unique_id = '{}-{}'.format(id, sensors[sensor_id])
        config_topic = '{}/sensor/{}-{}/config'.format(disc_prefix, id,
                                                       sensors[sensor_id])
        default_topic = 'shellies/{}/'.format(id)
        availability_topic = '~online'
        sensor_name = '{} {}'.format(device_name,
                                     sensors[sensor_id].capitalize())
        state_topic =  '~sensor/{}'.format(sensors[sensor_id])
        payload = '{\"name\":\"' + sensor_name + '\",' \
                  '\"stat_t\":\"' + state_topic + '\",' \
                  '\"unit_of_meas\":\"' + units[sensor_id] + '\",' \
                  '\"dev_cla\":\"' + sensors[sensor_id] + '\",' \
                  '\"val_tpl\":\"' + templates[sensor_id] + '\",' \
                  '\"avty_t\":\"' + availability_topic + '\",' \
                  '\"pl_avail\":\"true\",' \
                  '\"pl_not_avail\":\"false\",' \
                  '\"uniq_id\":\"' + unique_id + '\",' \
                  '\"dev\": {\"ids\": [\"' + mac + '\"],' \
                  '\"name\":\"' + device_name + '\",' \
                  '\"mdl\":\"' + model + '\",' \
                  '\"sw\":\"' + fw_ver + '\",' \
                  '\"mf\":\"Shelly\"},' \
                  '\"~\":\"' + default_topic + '\"}'
        service_data = {
            'topic': config_topic,
            'payload': payload,
            'retain': retain,
            'qos': 0
        }
        hass.services.call('mqtt', 'publish', service_data, False)
