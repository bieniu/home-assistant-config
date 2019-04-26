"""
This script adds MQTT discovery support for Shellies. Shelly1, Shelly1PM,
Shelly2, Shely2.5, Shelly4Pro, Shelly Plug, Shelly RGBW2, Shelly H&T, Shelly
Smoke and Shelly Sense are supported.

Arguments:
 - discovery_prefix:    - discovery prefix in HA, default 'homeassistant',
                          optional
 - id                   - Shelly ID (required)
 - mac                  - Shelly MAC address (required)
 - sensor               - sensor entity_id (required)
 - fw_ver               - Shelly firmware version (optional)
 - temp_unit            - C for Celsius, F for Farenhait, default C (optional)
 - list of shelies relays and components for them, only for devices with relays
                          (optional), by default all relays are added as
                          switches.

Default configuration
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
      id: '{{ trigger.payload_json.id }}'
      mac: '{{ trigger.payload_json.mac }}'
      fw_ver: '{{ trigger.payload_json.fw_ver }}'

If you want the relay to be a other component than the switch in the Home
Assistant, you have to add a description of the relay and its function to the
script configuration.
For example:
- id: 'shellies_discovery'
  alias: 'Shellies Discovery'
  trigger:
  - platform: mqtt
    topic: shellies/announce
  action:
    service: python_script.shellies_discovery
    data_template:
      id: '{{ trigger.payload_json.id }}'
      mac: '{{ trigger.payload_json.mac }}'
      fw_ver: '{{ trigger.payload_json.fw_ver }}'
      shellyswitch-334455-relay-0: 'cover'
      shelly1-001122-relay-0: 'light'

Argument shelly1-001122-relay-0: 'light' means that relay 0 of
shelly1-001122 will use light component in Home Assistant. You can use switch,
light or fan.
Argument shellyswitch-334455-relay-0: 'cover' means that Shelly2 works in
roller mode and use cover component in Home Assistant.

Script supports custom_updater component. Add this to your configuration and
stay up-to-date.

custom_updater:
  track:
    - python_scripts
  python_script_urls:
    - https://raw.githubusercontent.com/bieniu/home-assistant-config/master/python_scripts/python_scripts.json
"""

VERSION = '0.8.2'

ATTR_DEVELOP = 'develop'

ATTR_ID = 'id'
ATTR_MAC = 'mac'
ATTR_FW_VER = 'fw_ver'
ATTR_DISCOVERY_PREFIX = 'discovery_prefix'
ATTR_TEMP_UNIT = 'temp_unit'

ATTR_TEMPLATE_TEMPERATURE = '{{ value | float | round(1) }}'
ATTR_TEMPLATE_HUMIDITY = '{{ value | float | round(1) }}'
ATTR_TEMPLATE_LUX = '{{ value | float | round }}'
ATTR_TEMPLATE_POWER = '{{ value | float | round(1) }}'
ATTR_TEMPLATE_ENERGY = '{{ (value | float / 60 / 1000) | round(2) }}'
ATTR_TEMPLATE_BATTERY = '{{ value | float | round }}'

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

if id == '' or mac == '':
    logger.error("Expected id and mac as arguments.")
else:
    relays = 0
    rollers = 0    
    relay_components = ['switch', 'light', 'fan']
    config_component = 'switch'
    relays_sensors = []
    relays_sensors_units = []
    relays_sensors_templates = []
    relays_sensors_classes = []
    sensors = []
    sensors_units = []
    sensors_templates = []
    sensors_classes = []
    bin_sensors = []    
    bin_sensors_classes = []
    rgbw_lights = 0
    battery_powered = False

    if 'shelly1-' in id:
        model = 'Shelly1'
        relays = 1

    if 'shelly1pm-' in id:
        model = 'Shelly1PM'
        relays = 1
        relays_sensors = ['power', 'energy']
        relays_sensors_units = ['W', 'kWh']
        relays_sensors_classes = ['power', 'power']
        relays_sensors_templates = [
            ATTR_TEMPLATE_POWER,
            ATTR_TEMPLATE_ENERGY
        ]
        sensors = ['temperature']
        sensors_classes = sensors
        sensors_units = [temp_unit]
        sensors_templates = [ATTR_TEMPLATE_TEMPERATURE]

    if 'shellyswitch-' in id:
        model = 'Shelly2'
        relays = 2
        rollers = 1
        relays_sensors = ['power', 'energy']
        relays_sensors_units = ['W', 'kWh']
        relays_sensors_classes = ['power', 'power']
        relays_sensors_templates = [
            ATTR_TEMPLATE_POWER,
            ATTR_TEMPLATE_ENERGY
        ]

    if 'shellyswitch25-' in id:
        model = 'Shelly2.5'
        relays = 2
        rollers = 1
        relays_sensors = ['power', 'energy']
        relays_sensors_units = ['W', 'kWh']
        relays_sensors_classes = ['power', 'power']
        relays_sensors_templates = [
            ATTR_TEMPLATE_POWER,
            ATTR_TEMPLATE_ENERGY
        ]
        sensors = ['temperature']
        sensors_classes = sensors
        sensors_units = [temp_unit]
        sensors_templates = [ATTR_TEMPLATE_TEMPERATURE]

    if 'shellyplug-' in id:
        model = 'Shelly Plug'
        relays = 1
        relays_sensors = ['power', 'energy']
        relays_sensors_units = ['W', 'kWh']
        relays_sensors_classes = ['power', 'power']
        relays_sensors_templates = [
            ATTR_TEMPLATE_POWER,
            ATTR_TEMPLATE_ENERGY
        ]

    if 'shelly4pro-' in id:
        model = 'Shelly4Pro'
        relays = 4
        relays_sensors = ['power', 'energy']
        relays_sensors_units = ['W', 'kWh']
        relays_sensors_classes = ['power', 'power']
        relays_sensors_templates = [
            ATTR_TEMPLATE_POWER,
            ATTR_TEMPLATE_ENERGY
        ]

    if 'shellyht-' in id:
        model = 'Shelly H&T'
        sensors = ['temperature', 'humidity', 'battery']
        sensors_classes = sensors
        sensors_units = [temp_unit, '%', '%']
        sensors_templates = [
            ATTR_TEMPLATE_TEMPERATURE,
            ATTR_TEMPLATE_HUMIDITY,
            ATTR_TEMPLATE_BATTERY
        ]
        battery_powered = True

    if 'shellysmoke-' in id:
        model = 'Shelly Smoke'
        sensors = ['temperature', 'battery']
        sensors_classes = sensors
        sensors_units = [temp_unit, '%']
        sensors_templates = [
            ATTR_TEMPLATE_TEMPERATURE,                     
            ATTR_TEMPLATE_BATTERY
        ]
        bin_sensors = ['smoke']
        bin_sensors_classes = bin_sensors
        battery_powered = True

    if 'shellysense-' in id:
        model = 'Shelly Sense'
        sensors = ['temperature', 'humidity', 'lux', 'battery']
        sensors_classes = ['temperature', 'humidity', 'illuminance', 'battery']
        sensors_units = [temp_unit, '%', 'lx', '%']
        sensors_templates = [
            ATTR_TEMPLATE_TEMPERATURE,
            ATTR_TEMPLATE_HUMIDITY,
            ATTR_TEMPLATE_LUX,                     
            ATTR_TEMPLATE_BATTERY
        ]
        bin_sensors = ['motion', 'charger']
        bin_sensors_classes = ['motion', 'power']
        battery_powered = True

    if 'shellyrgbw2-' in id:
        model = 'Shelly RGBW2'
        rgbw_lights = 1
                     
    for roller_id in range(0, rollers):
        device_name = '{} {}'.format(model, id.split('-')[1])
        roller_name = '{} Roller {}'.format(device_name, roller_id)
        default_topic = 'shellies/{}/'.format(id)
        state_topic = '~roller/{}'.format(roller_id)
        command_topic =  '{}/command'.format(state_topic)
        position_topic =  '{}/pos'.format(state_topic)
        set_position_topic =  '{}/command/pos'.format(state_topic)
        availability_topic = '~online'
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
        device_name = '{} {}'.format(model, id.split('-')[1])
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
                for sensor_id in range(0, len(relays_sensors)):
                    unique_id = '{}-relay-{}'.format(id,
                        relays_sensors[sensor_id])
                    config_topic = '{}/sensor/{}-{}/config'.format(disc_prefix,
                        id, relays_sensors[sensor_id])
                    sensor_name = '{} {}'.format(device_name,
                        relays_sensors[sensor_id].capitalize())
                    state_topic =  '~relay/{}'.format(relays_sensors[sensor_id])
                    payload = '{\"name\":\"' + sensor_name + '\",' \
                        '\"stat_t\":\"' + state_topic + '\",' \
                        '\"unit_of_meas\":\"' + relays_sensors_units[sensor_id] + '\",' \
                        '\"dev_cla\":\"' + relays_sensors_classes[sensor_id] + '\",' \
                        '\"val_tpl\":\"' + relays_sensors_templates[sensor_id] + '\",' \
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
            for sensor_id in range(0, len(relays_sensors)):
                unique_id = '{}-relay-{}-{}'.format(id,
                    relays_sensors[sensor_id], relay_id)
                config_topic = '{}/sensor/{}-{}-{}/config'.format(disc_prefix,
                    id, relays_sensors[sensor_id], relay_id)
                sensor_name = '{} {} {}'.format(device_name,
                    relays_sensors[sensor_id].capitalize(), relay_id)
                state_topic =  '~relay/{}/{}'.format(relay_id,
                    relays_sensors[sensor_id])
                payload = '{\"name\":\"' + sensor_name + '\",' \
                    '\"stat_t\":\"' + state_topic + '\",' \
                    '\"unit_of_meas\":\"' + relays_sensors_units[sensor_id] + '\",' \
                    '\"dev_cla\":\"' + relays_sensors_classes[sensor_id] + '\",' \
                    '\"val_tpl\":\"' + relays_sensors_templates[sensor_id] + '\",' \
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
        device_name = '{} {}'.format(model, id.split('-')[1])
        unique_id = '{}-{}'.format(id, sensors[sensor_id])
        config_topic = '{}/sensor/{}-{}/config'.format(disc_prefix, id,
            sensors[sensor_id])
        default_topic = 'shellies/{}/'.format(id)
        availability_topic = '~online'
        sensor_name = '{} {}'.format(device_name,
            sensors[sensor_id].capitalize())
        if relays != 0:
            state_topic = '~{}'.format(sensors[sensor_id])
        else:
            state_topic =  '~sensor/{}'.format(sensors[sensor_id])
        if battery_powered:
            payload = '{\"name\":\"' + sensor_name + '\",' \
                '\"stat_t\":\"' + state_topic + '\",' \
                '\"unit_of_meas\":\"' + sensors_units[sensor_id] + '\",' \
                '\"dev_cla\":\"' + sensors_classes[sensor_id] + '\",' \
                '\"val_tpl\":\"' + sensors_templates[sensor_id] + '\",' \
                '\"uniq_id\":\"' + unique_id + '\",' \
                '\"dev\": {\"ids\": [\"' + mac + '\"],' \
                '\"name\":\"' + device_name + '\",' \
                '\"mdl\":\"' + model + '\",' \
                '\"sw\":\"' + fw_ver + '\",' \
                '\"mf\":\"Shelly\"},' \
                '\"~\":\"' + default_topic + '\"}'
        else:
            payload = '{\"name\":\"' + sensor_name + '\",' \
                '\"stat_t\":\"' + state_topic + '\",' \
                '\"unit_of_meas\":\"' + sensors_units[sensor_id] + '\",' \
                '\"dev_cla\":\"' + sensors_classes[sensor_id] + '\",' \
                '\"val_tpl\":\"' + sensors_templates[sensor_id] + '\",' \
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

    for bin_sensor_id in range(0, len(bin_sensors)):
        device_name = '{} {}'.format(model, id.split('-')[1])
        unique_id = '{}-{}'.format(id, bin_sensors[bin_sensor_id])
        config_topic = '{}/binary_sensor/{}-{}/config'.format(disc_prefix, id,
            bin_sensors[bin_sensor_id])
        default_topic = 'shellies/{}/'.format(id)
        availability_topic = '~online'
        sensor_name = '{} {}'.format(device_name,
            bin_sensors[bin_sensor_id].capitalize())
        state_topic =  '~sensor/{}'.format(bin_sensors[bin_sensor_id])
        if battery_powered:
            payload = '{\"name\":\"' + sensor_name + '\",' \
                '\"stat_t\":\"' + state_topic + '\",' \
                '\"pl_on\":\"true\",' \
                '\"pl_off\":\"false\",' \
                '\"dev_cla\":\"' + bin_sensors_classes[bin_sensor_id] + '\",' \
                '\"uniq_id\":\"' + unique_id + '\",' \
                '\"dev\": {\"ids\": [\"' + mac + '\"],' \
                '\"name\":\"' + device_name + '\",' \
                '\"mdl\":\"' + model + '\",' \
                '\"sw\":\"' + fw_ver + '\",' \
                '\"mf\":\"Shelly\"},' \
                '\"~\":\"' + default_topic + '\"}'
        else:            
            payload = '{\"name\":\"' + sensor_name + '\",' \
                '\"stat_t\":\"' + state_topic + '\",' \
                '\"pl_on\":\"true\",' \
                '\"pl_off\":\"false\",' \
                '\"avty_t\":\"' + availability_topic + '\",' \
                '\"pl_avail\":\"true\",' \
                '\"pl_not_avail\":\"false\",' \
                '\"dev_cla\":\"' + bin_sensors_classes[bin_sensor_id] + '\",' \
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

    for light_id in range(0, rgbw_lights):
        device_name = '{} {}'.format(model, id.split('-')[1])
        light_name = '{} Light'.format(device_name)
        default_topic = 'shellies/{}/'.format(id)
        state_topic = '~color/{}/status'.format(light_id)
        command_topic =  '{}/command'.format(state_topic)
        availability_topic = '~online'
        unique_id = '{}-light-{}'.format(id, light_id)
        config_topic = '{}/light/{}-{}/config'.format(disc_prefix, id, light_id)
        payload = '{\"schema\":\"template\",' \
            '\"name\":\"' + light_name + '\",' \
            '\"cmd_t\":\"' + command_topic + '\",' \
            '\"stat_t\":\"' + state_topic +'\",' \
            '\"avty_t\":\"' + availability_topic + '\",' \
            '\"pl_avail\":\"true\",' \
            '\"pl_not_avail\":\"false\",' \
            '\"fx_list\":[0, 1, 2, 3, 4, 5, 5],' \
            '\"command_on_template\":\"{\\"turn\\":\\"on\\"{% if brightness is defined %},\\"gain\\":{{ brightness | float | multiply(0.3922) | round(0) }}{% endif %}{% if red is defined and green is defined and blue is defined %},\\"red\\":{{ red }},\\"green\\":{{ green }},\\"blue\\":{{ blue }}{% endif %}{% if white_value is defined %},\\"white\\":{{ white_value }}{% endif %}{% if effect is defined %},\\"effect\\":{{ effect }}{% endif %}}\",' \
            '\"command_off_template\":\"{\\"turn\\":\\"off\\"}\",' \
            '\"state_template\":\"{% if value_json.ison %}on{% else %}off{% endif %}\",' \
            '\"brightness_template\":\"{{ value_json.gain | float | multiply(2.55) | round(0) }}\",' \
            '\"red_template\":\"{{ value_json.red }}\",' \
            '\"green_template\":\"{{ value_json.green }}\",' \
            '\"blue_template\":\"{{ value_json.blue }}\",' \
            '\"white_value_template\":\"{{ value_json.white }}\",' \
            '\"effect_template\":\"{{ value_json.effect }}\",' \
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