import appdaemon.appapi as appapi
from time import sleep

class UpdateThermostats(appapi.AppDaemon):

	def initialize(self):

		if len(self.args['thermostats']) != len(self.args['sensors']):
			raise Exception('Wrong arguments! The arguments sensors and thermostats must contain the same number of elements.')
		
		sleep(60) # time to initialize thermostats and sensors
		
		for i in range(len(self.args['thermostats'])):
			self.listen_state(self.update_thermostat_state, self.args['thermostats'][i], attribute = "current_temperature")
			self.listen_state(self.update_thermostat_state, self.args['sensors'][i])
			if self.get_state(self.args['thermostats'][i], attribute="current_temperature") == None:
				self.update_thermostat_state(self.args['thermostats'][i], attribute = None, old = None, new = None, kwargs = None)

	def update_thermostat_state(self, entity, attribute, old, new, kwargs):
		for i in range(len(self.args['thermostats'])):
			if entity == self.args['thermostats'][i] or entity == self.args['sensors'][i]:
				self.thermostat = self.args['thermostats'][i]
				self.sensor = self.args['sensors'][i]

		temperature = self.get_state(self.sensor)

		if temperature is not None and temperature != 'Unknown':
			if float(temperature) > 8:
				state = 'heat'
			else:
				state = 'idle'
			self.set_state(self.thermostat, state=state, attributes = {"current_temperature": temperature})
		else:
			self.log('No temperature data on the sensor {}.'.format(self.sensor))