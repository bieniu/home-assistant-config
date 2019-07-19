"""
Update Z-Wave thermostats (e.g. Danfoss 014G0013) state and current temperature
from sensor.
Arguments:
 - rooms           - list of rooms (required)
 - thermostat      - thermostat entity_id (required)
 - sensor          - temperature sensors entity_id (required)
 - heat_state      - name of heating state, default 'heat' (optional)
 - idle_state      - name of idle state, default 'off' (optional)
 - idle_heat_temp  - temperature value between 'idle' and 'heat' states,
                     default 8 (optional)
 - state_only      - with state_only set to 'true' app will update only
                     state of the thermostat, default false (optional)
 - temp_only       - with temp_only set to 'true' app will update only
                     current_temperature of the thermostat, default false
                     (optional)
 - wait_for_zwave  - defines whether the script has to wait for the
                     initialization of the Z-wave component
                     after Home Assistant restart, default True (optional)

Configuration example:

thermostats_update:
  module: thermostats-update
  class: ThermostatsUpdate
  rooms:
    kitchen:
      thermostat: climate.thermostat_kitchen
      sensor: sensor.temperature_kitchen
    room:
      thermostat: climate.thermostat_room
      sensor: sensor.temperature_room
    bathroom:
      thermostat: climate.thermostat_bathroom
      sensor: sensor.temperature.bathroom
  heat_state: 'auto'
  idle_state: 'idle'
  idle_heat_temp: 10
  state_only: true
  wait_for_zwave: true

"""

import appdaemon.plugins.hass.hassapi as hass


class ThermostatsUpdate(hass.Hass):

    def initialize(self):

        __version__ = '0.3.1'

        ATTR_HEAT_DEFAULT = 'heat'
        ATTR_OFF_DEFAULT = 'off'
        ATTR_DEBUG = 'debug'
        ATTR_LOG_DEBUG = 'DEBUG'
        ATTR_LOG_INFO = 'INFO'
        ATTR_IDLE_HEAT_TEMP_DEFAULT = 8
        ATTR_WAIT_FOR_ZWAVE = 'wait_for_zwave'
        ATTR_HEAT_STATE = 'heat_state'
        ATTR_IDLE_STATE = 'idle_state'
        ATTR_IDLE_HEAT_TEMP = 'idle_heat_temp'
        ATTR_STATE_ONLY = 'state_only'
        ATTR_TEMP_ONLY = 'temp_only'

        self.zwave_handle = None

        if ATTR_WAIT_FOR_ZWAVE in self.args:
            wait_for_zwave = self.args[ATTR_WAIT_FOR_ZWAVE]
        else:
            wait_for_zwave = True
        if ATTR_STATE_ONLY in self.args:
            self.state_only = self.args[ATTR_STATE_ONLY]
        else:
            self.state_only = False
        if ATTR_TEMP_ONLY in self.args:
            self.temp_only = self.args[ATTR_TEMP_ONLY]
        else:
            self.temp_only = False
        if self.temp_only and self.state_only:
            self.error("You can use state_only: true or temp_only: true not "
                       "both!")
            return
        if ATTR_HEAT_STATE in self.args:
            self.heat_state = self.args[ATTR_HEAT_STATE]
        else:
            self.heat_state = ATTR_HEAT_DEFAULT
        if ATTR_IDLE_STATE in self.args:
            self.idle_state = self.args[ATTR_IDLE_STATE]
        else:
            self.idle_state = ATTR_OFF_DEFAULT
        try:
            if ATTR_IDLE_HEAT_TEMP in self.args:
                self.idle_heat_temp = int(self.args[ATTR_IDLE_HEAT_TEMP])
            else:
                self.idle_heat_temp = ATTR_IDLE_HEAT_TEMP_DEFAULT
        except ValueError:
            self.error("Wrong arguments! Argument idle_heat_temp has to be "
                       "an integer.")
            return
        self.log_level = ATTR_LOG_DEBUG
        if ATTR_DEBUG in self.args:
            if self.args[ATTR_DEBUG]:
                self.log_level = ATTR_LOG_INFO

        if wait_for_zwave and not self.zwave_entities_ready():
            self.log("Waiting for zwave.network_ready event...")
            self.zwave_handle = self.listen_event(self.start_listen_states,
                                                  'zwave.network_ready')
        else:
            self.start_listen_states(event=None, data=None, kwargs=None)

    def start_listen_states(self, event, data, kwargs):
        if self.zwave_handle is not None:
            self.cancel_listen_event(self.zwave_handle)
        self.log("Checking thermostats and sensors...")
        try:
            for room in self.args['rooms']:
                thermostat = self.args['rooms'][room]['thermostat']
                if not self.entity_exists(thermostat):
                    self.error("Wrong arguments! Entity "
                               "{} does not exist.".format(thermostat))
                    return
                if not self.state_only:
                    sensor = self.args['rooms'][room]['sensor']
                    if not self.entity_exists(sensor):
                        self.error("Wrong arguments! Entity "
                                   "{} does not exist.".format(sensor))
                        return
                self.listen_state(self.thermostat_state_changed, thermostat,
                                    attribute='current_temperature', new=None)
                if not self.state_only:
                    self.listen_state(self.sensor_state_changed, sensor)
                if self.get_state(thermostat,
                                    attribute='current_temperature') is None:
                    self.thermostat_state_changed(
                        thermostat,
                        attribute='current_temperature',
                        old=None, new=None, kwargs=None)
            self.log("Ready for action...")
        except KeyError:
            self.error("Wrong arguments! You must supply a valid sensors/"
                       "thermostats entities for each room.")

    def thermostat_state_changed(self, entity, attribute, old, new, kwargs):
        if not self.state_only:
            for room in self.args['rooms']:
                if entity == self.args['rooms'][room]['thermostat']:
                    sensor_id = self.args['rooms'][room]['sensor']

        target_temp = self.get_state(entity, attribute='temperature')
        org_state = self.get_state(entity)
        if not self.state_only:
            sensor_temp = self.get_state(sensor_id)
            if sensor_temp and sensor_temp != 'unknown':
                if not new or (new != 'unknown'
                            and float(new) != float(sensor_temp)):
                    self.update_thermostat(entity, org_state, target_temp,
                                           sensor_temp)
            else:
                self.log("No temperature data on the sensor {}.".format(sensor_id))
        else:
            self.update_thermostat(entity, org_state, target_temp, None)

    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        for room in self.args['rooms']:
            if entity == self.args['rooms'][room]['sensor']:
                thermostat_id = self.args['rooms'][room]['thermostat']

        current_temp = self.get_state(thermostat_id,
                                      attribute='current_temperature')
        target_temp = self.get_state(thermostat_id, attribute='temperature')
        org_state = self.get_state(thermostat_id)
        if new and new != 'unknown':
            if not current_temp or (current_temp != 'unknown'
                                    and float(current_temp) != float(new)):
                self.update_thermostat(thermostat_id, org_state, target_temp,
                                       new)
        else:
            self.log("No temperature data on the sensor {}.".format(entity))

    def update_thermostat(self, entity, state, target_temp, current_temp):
        self.log("Updating state and current "
                 "temperature for {}...".format(entity), self.log_level)
        if current_temp:
            if not self.temp_only:
                self.set_state(
                    entity,
                    state=self.find_thermostat_state(float(target_temp)),
                    attributes={"current_temperature": current_temp})
            else:
                self.set_state(
                    entity, state=state,
                    attributes={"current_temperature": current_temp})
        else:
            self.set_state(
                entity,
                state=self.find_thermostat_state(float(target_temp)))

    def find_thermostat_state(self, target_temp):
        if target_temp > self.idle_heat_temp:
            return self.heat_state
        else:
            return self.idle_state

    def zwave_entities_ready(self):
        resault = True
        entities = self.get_state('zwave',)
        try:
            for entity in entities:
                if not entities[entity]['attributes']['is_ready']:
                    resault = False
        except KeyError:
            resault = False
        return resault
