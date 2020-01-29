"""
Adds sensor to HA with DuneHD media player current activity.
Arguments:
 - host			- hostname or IP address of the DuneHD media player (required)
 - interval		- interval scanning, default 60 sec. (optional)
 - use_mqtt     - use mqtt or add entity by AppDaemon (optional), default false
 - mac          - DuneHD MAC address to generate unique_id for MQTT Discovery
                  (optional)
 - model        - name of player model (optional)
 - retain       - retain true or false for MQTT, default false

Configuration example:

dune_activity:
  module: dune_activity
  class: DuneActivity
  host: !secret brother_hostname
  status_interval: 5
  use_mqtt: true
  mac: 00:11:22:33:44:55
  model: 'BD Prime 3.0'
  retain: true
"""

import json
import re
from datetime import datetime, timedelta

import hassapi as hass
import requests


class DuneActivity(hass.Hass):
    def initialize(self):

        __version__ = "0.2.5"

        self.URL_FORMAT = "http://{}/cgi-bin/do"
        self.ENTITY = "sensor.dune_activity"
        self.TOPIC = "dune/activity/{}"
        self.MANUFACTURER = "Dune"
        self.model = "Network Player"
        self.use_mqtt = False
        self.mac = None
        self.mac_simple = None
        self.retain = False
        try:
            if self.args["host"]:
                self.host = self.args["host"]
        except KeyError:
            self.error(
                "Wrong arguments! You must supply a valid DuneHD "
                "media player hostname or IP address."
            )
            return
        try:
            if "interval" in self.args:
                interval = int(self.args["interval"])
            else:
                interval = 60
        except ValueError:
            self.error("Wrong arguments! Argument interval has to be an " "integer.")
            return
        if "model" in self.args:
            self.model = self.args["model"]
        if "use_mqtt" in self.args:
            self.use_mqtt = self.args["use_mqtt"]
            if self.use_mqtt:
                if "retain" in self.args:
                    self.retain = self.args["retain"]
                if "mac" in self.args:
                    self.mac = self.args["mac"]
                    self.mac_simple = self.mac.replace(":", "").lower()
        self.run_every(
            self.update_activity, datetime.now() + timedelta(seconds=1), interval
        )

    def update_activity(self, kwargs):
        request = None
        try:
            request = requests.get(self.URL_FORMAT.format(self.host), timeout=2)
        except requests.exceptions.RequestException:
            pass
        if not request:
            state = "offline"
        elif request.status_code == 200:
            pattern = re.compile('.*name="player_state" value="(.*)"')
            try:
                state = re.findall(pattern, request.text)[0]
            except IndexError:
                return
        else:
            state = "offline"
        if self.use_mqtt:
            if self.mac_simple and not self.entity_exists(self.ENTITY):
                payload = {
                    "name": "Dune Activity",
                    "uniq_id": self.mac_simple + "-activity",
                    "stat_t": self.TOPIC.format("state"),
                    "dev": {
                        "ids": self.mac_simple,
                        "cns": [["mac", self.mac]],
                        "mf": self.MANUFACTURER,
                        "mdl": self.model,
                        "name": self.MANUFACTURER + " " + self.model,
                    },
                }
                self.call_service(
                    "mqtt/publish",
                    topic="homeassistant/sensor/" + self.TOPIC.format("config"),
                    payload=json.dumps(payload),
                    qos=0,
                    retain=True,
                )
            old_state = self.get_state(self.ENTITY)
            if old_state and old_state != state:
                self.call_service(
                    "mqtt/publish",
                    topic=self.TOPIC.format("state"),
                    payload=state,
                    qos=0,
                    retain=self.retain,
                )
        else:
            self.set_state(self.ENTITY, state=state)
