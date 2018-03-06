import appdaemon.appapi as appapi
from time import sleep

"""
Update Z-Wave thermostats (e.g. Danfoss 014G0013) state and current temperature from sensor.
Arguments:
 - thermostats: list of thermostats entities
 - sensors: list of sensors entities
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

"""

class UpdateThermostats(appapi.AppDaemon):

	def initialize(self):
		if len(self.args['thermostats']) != len(self.args['sensors']):
			raise Exception('Wrong arguments! The arguments sensors and thermostats must contain the same number of elements.')
		
		for i in range(len(self.args['thermostats'])):
			if self.check_entity(self.args['thermostats'][i]) == False:
				raise Exception('Wrong arguments! At least one of the entities does not exist.')
			self.listen_state(self.thermostat_state_changed, self.args['thermostats'][i], attribute = "current_temperature")
			if self.check_entity(self.args['sensors'][i]) == False:
				raise Exception('Wrong arguments! At least one of the entities does not exist.')
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

	def find_thermostat_state(self, temperature):
		if temperature > 8:
			self.state = 'heat'
		else:
			self.state = 'idle'

	def check_entity(self, entity):
		n = 0
		while not (self.entity_exists(entity) or n > 120):
			n += 1
			sleep(1)
		if n > 120:
			return False
		else:
			return True