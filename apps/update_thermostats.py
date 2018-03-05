import appdaemon.appapi as appapi

class UpdateThermostats(appapi.AppDaemon):

	def initialize(self):

		if len(self.args['thermostats']) != len(self.args['sensors']):
			raise Exception('Wrong arguments! The arguments sensors and thermostats must contain the same number of elements.')

		for i in range(len(self.args['thermostats'])):
			if not self.entity_exists(self.args['thermostats'][i]) or not self.entity_exists(self.args['sensors'][i]):
				raise Exception('Wrong arguments! Arguments contain non-existent in Home Assistant entity.')

		for i in range(len(self.args['thermostats'])):
			self.listen_state(self.update_thermostat_state, self.args['thermostats'][i], attribute = "current_temperature")
			self.listen_state(self.update_thermostat_state, self.args['sensors'][i])

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
			# self.log('{} state updated'.format(self.thermostat))
