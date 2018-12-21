"""
Adds four sensors to HA with data from Brother network printer WWW interface.
Tested only with Brother HL-L2340DW.
Arguments:
 - host					- hostname or IP address of the printer (required)
 - status_interval		- interval scanning for status page, default 10 sec.,
                          status and toner sensors (optional)
 - info_interval		- interval scanning for information page, default 300
                          sec., printer counter and drum usage sensors
                          (optional)
 - use_mqtt             - use mqtt or add entities by AppDaemon (optional),
                          default false
 - mac                  - printer MAC address to generate unique_id for
                          MQTT Discovery (optional)
 - retain               - retain true or false for MQTT, default false

Configuration example:

brother_printer_status:
  module: brother_printer_status
  class: BrotherPrinterStatus
  host: !secret brother_hostname
  status_interval: 5
  info_interval: 600
  use_mqtt: true
  mac: 00:11:22:33:44:55
  retain: true
"""

import appdaemon.plugins.hass.hassapi as hass
import requests
from datetime import datetime
import re
import json


class BrotherPrinterStatus(hass.Hass):

    def initialize(self):

        __version__ = '0.3.1'

        # max value of the height of the black image on the printer's webpage
        self.MAX_IMAGE_HEIGHT = 56
        self.INFO_URL = "/general/information.html"
        self.STATUS_URL = "/general/status.html"
        self.TOPIC = "homeassistant/sensor/printer/{}/"
        self.SENSOR_PREFIX = "sensor.printer_{}"
        self.MANUFACTURER = 'Brother'
        self.use_mqtt = False
        self.mac = None
        self.mac_simple = None
        self.retain = False

        try:
            if self.args['host']:
                self.host = self.args['host']
        except KeyError:
            self.error("Wrong arguments! You must supply a valid printer "
                       "hostname or IP address.")
            return
        try:
            if 'status_interval' in self.args:
                status_interval = int(self.args['status_interval'])
            else:
                status_interval = 10
        except ValueError:
            self.error("Wrong arguments! Argument status_interval has to be "
                       "an integer.")
            return
        try:
            if 'info_interval' in self.args:
                info_interval = int(self.args['info_interval'])
            else:
                info_interval = 300
        except ValueError:
            self.error("Wrong arguments! Argument info_interval has to be "
                       "an integer.")
            return
        if 'use_mqtt' in self.args:
            self.use_mqtt = self.args['use_mqtt']
            if self.use_mqtt:
                if 'retain' in self.args:
                    self.retain = self.args['retain']
                if 'mac' in self.args:
                    self.mac = self.args['mac']
                    self.mac_simple = self.mac.replace(':', '').lower()

        self.run_every(self.update_printer_status_page, datetime.now(),
                       status_interval)
        self.run_every(self.update_printer_info_page, datetime.now(),
                       info_interval)

    def update_printer_status_page(self, kwargs):
        page = self.download_page("http://{}{}".format(self.host,
                                                       self.STATUS_URL))

        if page:
            regex_res = self.regex(r"<dd>.*>(\w+\s?\w+)\s+<.*</dd>", page)
            if regex_res:
                status = regex_res.lower()
                if status:
                    sensor = 'status'
                    entity = self.SENSOR_PREFIX.format(sensor)
                    if self.use_mqtt:
                        topic = self.TOPIC.format(sensor)
                        model = self.printer_model(page)
                        payload = {
                            "name": "Printer " + sensor,
                            "unique_id": self.mac_simple + "-" + sensor,
                            "device": {
                                "identifiers": self.mac_simple,
                                "connections": [["mac", self.mac]],
                                "manufacturer": self.MANUFACTURER,
                                "model": model,
                                "name": self.MANUFACTURER + ' ' + model
                            },
                            "icon": "mdi:printer",
                            "state_topic": topic + "state"
                        }
                        self.mqtt_publish(topic, payload, entity, sensor,
                                          status)
                    else:
                        attributes = {"friendly_name": "Printer status",
                                      "icon": "mdi:printer"}
                        self.set_state(entity, state=status,
                                       attributes=attributes)
            regex_res = self.regex(r"class=\"tonerremain\" height=\"(\d+)\"",
                                   page)
            if regex_res:
                try:
                    toner = round(int(regex_res) / self.MAX_IMAGE_HEIGHT * 100)
                except TypeError:
                    return
                if toner:
                    sensor = 'toner'
                    entity = self.SENSOR_PREFIX.format(sensor)
                    if self.use_mqtt:
                        topic = self.TOPIC.format(sensor)
                        model = self.printer_model(page)
                        payload = {
                            "name": "Printer " + sensor,
                            "unique_id": self.mac_simple + "-" + sensor,
                            "device": {
                                "identifiers": self.mac_simple,
                                "connections": [["mac", self.mac]],
                                "manufacturer": self.MANUFACTURER,
                                "model": model,
                                "name": self.MANUFACTURER + ' ' + model
                            },
                            "icon": "mdi:flask-outline",
                            "unit_of_measurement": "%",
                            "state_topic": topic + "state"
                        }
                        self.mqtt_publish(topic, payload, entity, sensor,
                                          toner)
                    else:
                        attributes = {"friendly_name": "Printer " + sensor,
                                      "icon": "mdi:flask-outline",
                                      "unit_of_measurement": "%"}
                        self.set_state(entity, state=toner,
                                       attributes=attributes)

    def update_printer_info_page(self, kwargs):
        page = self.download_page("http://{}{}".format(self.host,
                                                       self.INFO_URL))
        if page:
            regex_res = self.regex(r"<dd>(\d+)</dd>", page)
            if regex_res:
                try:
                    counter = int(regex_res)
                except TypeError:
                    return
                if counter:
                    sensor = 'counter'
                    entity = self.SENSOR_PREFIX.format(sensor)
                    if self.use_mqtt:
                        topic = self.TOPIC.format(sensor)
                        model = self.printer_model(page)
                        payload = {
                            "name": "Printer " + sensor,
                            "unique_id": self.mac_simple + "-" + sensor,
                            "device": {
                                "identifiers": self.mac_simple,
                                "connections": [["mac", self.mac]],
                                "manufacturer": self.MANUFACTURER,
                                "model": model,
                                "name": self.MANUFACTURER + ' ' + model
                            },
                            "icon": "mdi:file-document",
                            "unit_of_measurement": "p",
                            "state_topic": topic + "state"
                        }
                        self.mqtt_publish(topic, payload, entity, sensor,
                                          counter)
                    else:
                        attributes = {"friendly_name": "Printer " + sensor,
                                      "icon": "mdi:file-document",
                                      "unit_of_measurement": "p"}
                        self.set_state(entity, state=counter,
                                       attributes=attributes)
            regex_res = self.regex(r"\((\d+\.\d+)%\)", page)
            if regex_res:
                try:
                    drum_usage = round(100 - float(regex_res))
                except TypeError:
                    return
                if drum_usage:
                    sensor = 'drum-usage'
                    entity = self.SENSOR_PREFIX.format(sensor.replace('-', '_'))
                    if self.use_mqtt:
                        topic = self.TOPIC.format(sensor)
                        model = self.printer_model(page)
                        payload = {
                            "name": "Printer " + sensor.replace('-', ' '),
                            "unique_id": self.mac_simple + "-" + sensor,
                            "device": {
                                "identifiers": self.mac_simple,
                                "connections": [["mac", self.mac]],
                                "manufacturer": self.MANUFACTURER,
                                "model": model,
                                "name": self.MANUFACTURER + ' ' + model
                            },
                            "icon": "mdi:chart-donut",
                            "unit_of_measurement": "%",
                            "state_topic": topic + "state"
                        }
                        self.mqtt_publish(topic, payload, entity, sensor,
                                          drum_usage)
                    else:
                        attributes = {"friendly_name": "Printer " +
                                                       sensor.replace('-', ' '),
                                      "icon": "mdi:chart-donut",
                                      "unit_of_measurement": "%"}
                        self.set_state(entity, state=drum_usage,
                                       attributes=attributes)

    def download_page(self, url):
        page = None
        try:
            page = requests.get(url, timeout=2)
        except requests.exceptions.RequestException:
            self.error("Host {} unreachable or respond too "
                       "slow!".format(self.host))
            return
        return page.text

    def regex(self, pattern, text):
        resault = re.findall(pattern, text)
        if len(resault) > 0:
            return resault[0]
        return None

    def mqtt_publish(self, topic, payload, entity, sensor, new_state):
        if self.mac_simple and not self.entity_exists(entity):
            self.call_service("mqtt/publish",  topic=topic+"config",
                              payload=json.dumps(payload), qos=0,
                              retain=self.retain)
        old_state = self.get_state(entity)
        if old_state and str(old_state) != str(new_state):
            self.call_service("mqtt/publish", topic=topic+"state",
                              payload=new_state, qos=0, retain=self.retain)

    def printer_model(self, page):
        model = 'Printer'
        regex_res = self.regex(r"<title>Brother\s(.+)\sseries</title>", page)
        if regex_res:
            model = regex_res
        return model
