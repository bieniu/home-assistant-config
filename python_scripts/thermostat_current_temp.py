thermostat_id  = data.get('thermostat')
sensor_id  = data.get('sensor')

if thermostat_id != "" and sensor_id != "":
   sensor = hass.states.get(sensor_id)
   temp = sensor.state
   thermostat = hass.states.get(thermostat_id)
   attributes = thermostat.attributes.copy()
   attributes['current_temperature'] = temp
   hass.states.set(thermostat_id, thermostat.state, attributes)
else:
   logger.error("Wrong data.")

