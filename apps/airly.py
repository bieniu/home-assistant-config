"""
Adds to HA sensors with data from Airly.
 - airly_apikey - Airly API key (required)
 - latitude     - latitude (required)
 - longitude    - longitude (required)
 - retain       - retain true or false for MQTT, default false (optional)
 - interval     - update interval, default 5 min. (optional)
 - sensors      - dictionary of sensors to add, default pm1, pm25, pm10, caqi
                  (optional), available sensors: pm1, pm25, pm10, caqi,
                  temperature, humidity, pressure

Configuration example:

airly:
  module: airly
  class: Airly
  airly_apikey: 12345678910
  latitude: 52.2323788
  longitude: 21.0439212
  retain: false
  interval: 10
  sensors:
    - pm1
    - pm25
    - pm10
    - caqi
    - temperature
    - humidity
    - pressure
"""

import appdaemon.plugins.hass.hassapi as hass
import requests
import json
from datetime import datetime

class Airly(hass.Hass):

    def initialize(self):

        __version__ = '0.0.1'

        ATTR_DISCOVERY_PREFIX = 'discovery_prefix'
        ATTR_AIRLY_APIKEY = 'airly_apikey'
        ATTR_LATITUDE = 'latitude'
        ATTR_LONGITUDE = 'longitude'
        ATTR_RETAIN = 'retain'
        ATTR_INTERVAL = 'interval'
        ATTR_SENSORS = 'sensors'
        self.ATTR_PM1 = 'pm1'
        self.ATTR_PM25 = 'pm25'
        self.ATTR_PM10 = 'pm10'
        self.ATTR_CAQI = 'caqi'
        self.ATTR_TEMPERATURE = 'temperature'
        self.ATTR_HUMIDITY = 'humidity'
        self.ATTR_PRESSURE = 'pressure'
        ATTR_NO_SENSOR_AVAILABLE = ("There are no Airly sensors in this area "
                                   "yet.")
        AVAILABLE_SENSORS = [self.ATTR_PM1, self.ATTR_PM25, self.ATTR_PM10,
                             self.ATTR_CAQI, self.ATTR_TEMPERATURE,
                             self.ATTR_HUMIDITY, self.ATTR_PRESSURE]

        discovery_prefix = 'homeassistant'
        self.retain = False
        interval = 5
        self.sensors = [self.ATTR_PM1, self.ATTR_PM25, self.ATTR_PM10,
                        self.ATTR_CAQI]

        try:
            if self.args[ATTR_AIRLY_APIKEY]:
                self.apikey = self.args[ATTR_AIRLY_APIKEY]
        except KeyError:
            self.error("Wrong arguments! You must supply a valid Airly API "
                       "key.")
            return
        try:
            if self.args[ATTR_LATITUDE]:
                self.latitude = self.args[ATTR_LATITUDE]
        except KeyError:
            self.error("Wrong arguments! You must supply a valid latitude.")
            return
        try:
            if self.args[ATTR_LONGITUDE]:
                self.longitude = self.args[ATTR_LONGITUDE]
        except KeyError:
            self.error("Wrong arguments! You must supply a valid longitude.")
            return
        try:
            if self.args[ATTR_DISCOVERY_PREFIX]:
                discovery_prefix = self.args[ATTR_DISCOVERY_PREFIX]
        except KeyError:
            pass
        try:
            if self.args[ATTR_RETAIN]:
                if isinstance(self.args[ATTR_RETAIN], bool):
                    self.retain = self.args[ATTR_RETAIN]
                else:
                    self.error("Wrong arguments! retain has to be boolean.")
                    return
        except KeyError:
            pass
        try:
            if self.args[ATTR_INTERVAL]:
                interval = int(self.args[ATTR_INTERVAL])
        except KeyError:
            pass
        except ValueError:
            self.error("Wrong arguments! Scan_update has to be an integer.")
            return
        try:
            if self.args[ATTR_SENSORS]:
                for sensor in self.args[ATTR_SENSORS]:
                    if not sensor in AVAILABLE_SENSORS:
                        self.error("Wrong arguments! {} is not an available "
                                   "sensor.".format(sensor))
                        return
                    self.sensors = self.args[ATTR_SENSORS]
        except KeyError:
            pass
        self.url = ('https://airapi.airly.eu/v2/measurements/point?lat={}&lng='
                    '{}&maxDistanceKM=5'.format(self.latitude, self.longitude))
        self.unique = '{}-{}'.format(self.latitude, self.longitude)
        self.headers = {'Accept': 'application/json',
                        'apikey': self.apikey}

        request = requests.get(self.url, headers=self.headers)
        try:
            if request.json()['errorCode']:
                self.error("Wrong arguments! Airly error "
                           "code {}.".format(request.json()['errorCode']))
                return
        except KeyError:
            pass
        try:
            if (request.json()['current']['indexes'][0]['description'] ==
               ATTR_NO_SENSOR_AVAILABLE):
               self.error(ATTR_NO_SENSOR_AVAILABLE)
               return
        except KeyError:
            pass

        for sensor in self.sensors:
            unit = None
            icon = None
            device_class = None
            attr_topic = None
            topic = '{}/sensor/airly/{}/{}/config'.format(discovery_prefix,
                                                          self.unique, sensor)
            state_topic = "airly/{}/{}/state".format(self.unique, sensor)
            unique_id = "airly-{}-{}".format(self.unique, sensor)
            if sensor == self.ATTR_PM1:
                unit = 'ug/m3'
                icon = 'mdi:blur'
                name = "Airly {}".format(sensor.upper())
                payload = {
                    "name": name,
                    "unique_id": unique_id,
                    "state_topic": state_topic,
                    "unit_of_measurement": unit,
                    "icon": icon
                    }
            elif sensor == self.ATTR_PM25:
                unit = 'ug/m3'
                icon = 'mdi:blur'
                name = "Airly {}".format(sensor.upper())
                attr_topic = "airly/{}/{}/attr".format(self.unique, sensor)
                payload = {
                    "name": name,
                    "unique_id": unique_id,
                    "state_topic": state_topic,
                    "unit_of_measurement": unit,
                    "icon": icon,
                    "json_attributes_topic": attr_topic
                    }
            elif sensor == self.ATTR_PM10:
                unit = 'ug/m3'
                icon = 'mdi:blur'
                name = "Airly {}".format(sensor.upper())
                attr_topic = "airly/{}/{}/attr".format(self.unique, sensor)
                payload = {
                    "name": name,
                    "unique_id": unique_id,
                    "state_topic": state_topic,
                    "unit_of_measurement": unit,
                    "icon": icon,
                    "json_attributes_topic": attr_topic
                    }
            elif sensor == self.ATTR_CAQI:
                name = "Airly {}".format(sensor.upper())
                attr_topic = "airly/{}/{}/attr".format(self.unique, sensor)
                payload = {
                    "name": name,
                    "unique_id": unique_id,
                    "state_topic": state_topic,
                    "json_attributes_topic": attr_topic
                    }
            elif sensor == self.ATTR_TEMPERATURE:
                unit = 'C'
                device_class = sensor
                name = "Airly {}".format(sensor.capitalize())
                payload = {
                    "name": name,
                    "unique_id": unique_id,
                    "state_topic": state_topic,
                    "unit_of_measurement": unit,
                    "device_class": device_class,
                    }
            elif sensor == self.ATTR_HUMIDITY:
                unit = '%'
                device_class = sensor
                name = "Airly {}".format(sensor.capitalize())
                payload = {
                    "name": name,
                    "unique_id": unique_id,
                    "state_topic": state_topic,
                    "unit_of_measurement": unit,
                    "device_class": device_class,
                    }
            elif sensor == self.ATTR_PRESSURE:
                unit = 'hPa'
                device_class = sensor
                name = "Airly {}".format(sensor.capitalize())
                payload = {
                    "name": name,
                    "unique_id": unique_id,
                    "state_topic": state_topic,
                    "unit_of_measurement": unit,
                    "device_class": device_class,
                    }

            self.call_service("mqtt/publish", topic=topic,
                              payload=json.dumps(payload), qos=0, retain=False) # docelowo zmienić retain na True
        self.run_every(self.update, datetime.now(), interval * 60)

    def update(self, kwargs):
        request = None
        try:
            request = requests.get(self.url, headers=self.headers)
        except requests.exceptions.RequestException:
            self.error("Data download error!")

        for sensor in self.sensors:
            attr_payload = None
            topic = 'airly/{}/{}/{}'
            if sensor == self.ATTR_PM1:
                payload = (round(request.json()['current']['values'][0]
                           ['value']))
            elif sensor == self.ATTR_PM25:
                payload = (round(request.json()['current']['values'][1]
                           ['value']))
                attr_payload = {
                    "limit": (round(request.json()['current']['standards'][0]
                              ['limit'])),
                    "percent": (round(request.json()['current']['standards'][0]
                                ['percent']))
                    }
            elif sensor == self.ATTR_PM10:
                payload = (round(request.json()['current']['values'][2]
                           ['value']))
                attr_payload = {
                    "limit": (round(request.json()['current']['standards'][1]
                              ['limit'])),
                    "percent": (round(request.json()['current']['standards'][1]
                                ['percent']))
                    }
            elif sensor == self.ATTR_CAQI:
                payload = (round(request.json()['current']['indexes'][0]
                           ['value']))
                attr_payload = {
                    "level": (request.json()['current']['indexes'][0]
                              ['level'].lower())
                    }
            elif sensor == self.ATTR_TEMPERATURE:
                payload = (round(request.json()['current']['values'][5]
                           ['value'], 1))
            elif sensor == self.ATTR_HUMIDITY:
                payload = (round(request.json()['current']['values'][4]
                           ['value'], 1))
            elif sensor == self.ATTR_PRESSURE:
                payload = (round(request.json()['current']['values'][3]
                           ['value']))

            self.call_service("mqtt/publish", topic=topic.format(self.unique,
                              sensor, 'state'), payload=payload, qos=0,
                              retain=self.retain)
            if attr_payload:
                self.call_service("mqtt/publish",
                                  topic=topic.format(self.unique, sensor,
                                  'attr'), payload=json.dumps(attr_payload),
                                  qos=0, retain=self.retain)
