"""
Update Z-Wave thermostats (e.g. Danfoss 014G0013) state and current temperature from external sensor.
Arguments:
 - thermostat			- thermostat entity_id
 - sensor				- sensor entity_id
 - heat_state			- name of heating state, default 'heat' (optional)
 - idle_state			- name of idle state, default 'idle' (optional)
 - idle_heat_temp		- temperature value between 'idle' and 'heat' states, default 8 (optional)

Configuration example:

service: python_script.update_thermostat
data:
  thermostat: climate.thermostat_kitchen
  sensor: sensor.temperature_kitchen
  heat_stat: 'auto'
  idle_state: 'off'
  idle_heat_temp: 10
"""
thermostat_id  = data.get('thermostat')
sensor_id  = data.get('sensor')
heat_state = data.get('heat_state', 'heat')
idle_state = data.get('idle_state', 'idle')
idle_heat_temp = data.get('idle_heat_temp', 8)

if thermostat_id is not None and sensor_id is not None:
	temp = hass.states.get(sensor_id).state
	if temp is not None and temp is not 'unknown':
		thermostat = hass.states.get(thermostat_id)
		attributes = thermostat.attributes.copy()
		attributes['current_temperature'] = temp
		if float(attributes['temperature']) > idle_heat_temp:
			state = heat_state
		else:
			state = idle_state
		hass.states.set(thermostat_id, state, attributes)
else:
	logger.error('Wrong arguments!')

