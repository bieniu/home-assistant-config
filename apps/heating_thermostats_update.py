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
 - wait_for_zwave  - defines whether the script has to wait for the
                     initialization of the Z-wave component
                     after Home Assistant restart, default True (optional)

Configuration example:

heating_thermostats_update:
  module: heating_thermostats_update
  class: HeatingThermostatsUpdate
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
  wait_for_zwave: true

"""

import appdaemon.plugins.hass.hassapi as hass


class HeatingThermostatsUpdate(hass.Hass):

    def initialize(self):

        __version__ = '0.2.6'

        self.zwave_handle = None

        if 'wait_for_zwave' in self.args:
            wait_for_zwave = self.args['wait_for_zwave']
        else:
            wait_for_zwave = True
        if 'heat_state' in self.args:
            self.heat_state = self.args['heat_state']
        else:
            self.heat_state = 'heat'
        if 'idle_state' in self.args:
            self.idle_state = self.args['idle_state']
        else:
            self.idle_state = 'off'
        try:
            if 'idle_heat_temp' in self.args:
                self.idle_heat_temp = int(self.args['idle_heat_temp'])
            else:
                self.idle_heat_temp = 8
        except ValueError:
            self.error("Wrong arguments! Argument idle_heat_temp has to be "
                       "an integer.")
            return
        self.log_level = 'DEBUG'
        if 'debug' in self.args:
            if self.args['debug']:
                self.log_level = 'INFO'

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
                sensor = self.args['rooms'][room]['sensor']
                if not self.entity_exists(thermostat) or \
                   not self.entity_exists(sensor):
                    self.error("Wrong arguments! At least one of the "
                               "entities does not exist.")
                    return
                self.listen_state(self.thermostat_state_changed, thermostat,
                                  attribute='current_temperature', new=None)
                self.listen_state(self.sensor_state_changed, sensor)
                if self.get_state(thermostat,
                                  attribute='current_temperature') is None:
                    self.thermostat_state_changed(
                                               thermostat,
                                               attribute='current_temperature',
                                               old=None, new=None, kwargs=None)
            self.log("Ready for action...")
        except KeyError:
            self.error("Wrong arguments! You must supply a valid sensors and "
                       "thermostats entities for each room.")

    def thermostat_state_changed(self, entity, attribute, old, new, kwargs):
        for room in self.args['rooms']:
            if entity == self.args['rooms'][room]['thermostat']:
                sensor_id = self.args['rooms'][room]['sensor']

        sensor_temp = self.get_state(sensor_id)
        target_temp = self.get_state(entity, attribute='temperature')

        if sensor_temp and sensor_temp != 'unknown':
            if not new or (new != 'unknown'
                           and float(new) != float(sensor_temp)):
                self.update_thermostat(entity, target_temp, sensor_temp)
        else:
            self.log("No temperature data on the sensor {}.".format(sensor_id))

    def sensor_state_changed(self, entity, attribute, old, new, kwargs):
        for room in self.args['rooms']:
            if entity == self.args['rooms'][room]['sensor']:
                thermostat_id = self.args['rooms'][room]['thermostat']

        current_temp = self.get_state(thermostat_id,
                                      attribute='current_temperature')
        target_temp = self.get_state(thermostat_id, attribute='temperature')

        if new and new != 'unknown':
            if not current_temp or (current_temp != 'unknown'
                                    and float(current_temp) != float(new)):
                self.update_thermostat(thermostat_id, target_temp, new)
        else:
            self.log("No temperature data on the sensor {}.".format(entity))

    def update_thermostat(self, entity, target_temp, current_temp):
            self.log("Updating state and current "
                     "temperature for {}...".format(entity), self.log_level)
            self.set_state(
                          entity,
                          state=self.find_thermostat_state(float(target_temp)),
                          attributes={"current_temperature": current_temp})

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
