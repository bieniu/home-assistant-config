"""
Update Z-Wave thermostats (e.g. Danfoss 014G0013) state and current temperature from sensor.
Arguments:
 - thermostats			- list of thermostats entities
 - sensors				- list of sensors entities
 - heat_state			- name of heating state, default 'heat'
 - idle_state			- name of idle state, default 'idle'
 - idle_heat_temp		- temperature value between 'idle' and 'heat' states, default 8
The order of thermostats and sensors is important. The first thermostat takes data from the first sensor, the second thermostat from the second sensor, etc.

Configuration example:

update_thermostats:
  module: update_thermostats
  class: UpdateThermostats
  thermostats:
    - climate.thermostat_kitchen
    - climate.thermostat_room
    - climate.thermostat_bathroom
  sensors:
    - sensor.temperature_kitchen
    - sensor.temperature_room
    - sensor.temperature_bathroom
  heat_state: auto
  idle_state: off
  idle_heat_temp: 10

"""

import appdaemon.appapi as appapi
from time import sleep

class UpdateThermostats(appapi.AppDaemon):

	def initialize(self):
		if len(self.args['thermostats']) != len(self.args['sensors']):
			raise Exception('Wrong arguments! The arguments sensors and thermostats must contain the same number of elements.')
		
		self.HEAT_STATE = 'heat'
		self.IDLE_STATE = 'idle'
		self.IDLE_HEAT_TEMP = 8
		
		if self.args['heat_state'] is not None:
			self.HEAT_STATE = self.args['heat_state']
		if self.args['idle_state'] is not None:
			self.IDLE_STATE = self.args['idle_state']
		if self.args['idle_heat_temp'] is not None:
			self.IDLE_HEAT_TEMP = float(self.args['idle_heat_temp'])

		for i in range(len(self.args['thermostats'])):
			if self.check_entity(self.args['thermostats'][i]) == False:
				raise Exception('Wrong arguments! At least one of the entities does not exist.')
			if self.check_entity(self.args['sensors'][i]) == False:
				raise Exception('Wrong arguments! At least one of the entities does not exist.')
			self.listen_state(self.thermostat_state_changed, self.args['thermostats'][i], attribute = "current_temperature", new = None)
			self.listen_state(self.sensor_state_changed, self.args['sensors'][i])
			if self.get_state(self.args['thermostats'][i], attribute="current_temperature") == None:
				self.thermostat_state_changed(self.args['thermostats'][i], attribute = "current_temperature", old = None, new = None, kwargs = None)

	def thermostat_state_changed(self, entity, attribute, old, new, kwargs):
		for i in range(len(self.args['thermostats'])):
			if entity == self.args['thermostats'][i]:
				sensor_id = self.args['sensors'][i]

		sensor_temp = self.get_state(sensor_id)
		target_temp = self.get_state(entity, attribute="temperature")

		if new == None or float(new) != float(sensor_temp):
			if sensor_temp is not None and sensor_temp != 'Unknown':
				self.find_thermostat_state(float(target_temp))
				self.set_state(entity, state=self.state, attributes = {"current_temperature": sensor_temp})
			else:
				self.log('No temperature data on the sensor {}.'.format(sensor_id))

	def sensor_state_changed(self, entity, attribute, old, new, kwargs):
		for i in range(len(self.args['sensors'])):
			if entity == self.args['sensors'][i]:
				thermostat_id = self.args['thermostats'][i]

				current_temp = self.get_state(thermostat_id, attribute="current_temperature")
		target_temp = self.get_state(thermostat_id, attribute="temperature")

		if current_temp == None or float(current_temp) != float(new):
			if new is not None and new != 'Unknown':
				self.find_thermostat_state(float(target_temp))
				self.set_state(thermostat_id, state=self.state, attributes = {"current_temperature": new})
			else:
				self.log('No temperature data on the sensor {}.'.format(self.entity))

	def find_thermostat_state(self, target_temp):
		if target_temp > self.IDLE_HEAT_TEMP:
			self.state = self.HEAT_STATE
		else:
			self.state = self.IDLE_STATE

	def check_entity(self, entity):
		n = 0
		while not (self.entity_exists(entity) or n > 120):
			n += 1
			sleep(1)
		if n > 120:
			return False
		else:
			return True