"""
Adds four sensors to HA with data from brother network printer WWW interface. Tested only with Brother HL-L2340DW.
Arguments:
 - host					- hostname or IP address of the printer (required)
 - status_interval		- interval scanning for status page, default 5 sec. [status and toner sensors] (optional)
 - info_interval		- interval scanning for information page, default 300 sec. [printed pages and drum usage sensors] (optional)

Required install
 - BeautifulSoup [pip3 install beautifulsoup4]

Configuration example:

brother_printer_status:
  module: brother_printer_status
  class: BrotherPrinterStatus
  host: !secret brother_hostname
  status_interval: 5
  info_interval: 600

"""

import appdaemon.plugins.hass.hassapi as hass
from bs4 import BeautifulSoup
from requests import get
from datetime import datetime

class BrotherPrinterStatus(hass.Hass):

    def initialize(self):

        __version__ = '0.1.3'

        self.MAX_IMAGE_HEIGHT = 56
        self.INFO_URL = '/general/information.html'
        self.STATUS_URL = '/general/status.html'

        try:
            if self.args['host'] is not None:
                self.HOST = self.args['host']
        except KeyError:
            self.error('Wrong arguments! You must supply a valid printer hostname or IP address.')
            return
        if 'status_interval' in self.args:
            status_interval = int(self.args['status_interval'])
        else:
            status_interval = 10
        if 'info_interval' in self.args:
            info_interval = int(self.args['info_interval'])
        else:
            info_interval = 300
        self.run_every(self.update_printer_status_page, datetime.now(), status_interval)
        self.run_every(self.update_printer_info_page, datetime.now(), info_interval)

    def update_printer_status_page(self, kwargs):
        self.download_page('http://{}{}'.format(self.HOST, self.STATUS_URL))
        if self.page is not None:
            soup = BeautifulSoup(self.page.text, 'html.parser')
            tag = soup.find_all('dd')[0]
            status = tag.string.lower()
            attributes = {"friendly_name": "Status drukarki", "icon": "mdi:printer"}
            self.update_sensor('sensor.printer_status', status, attributes)
            tag = soup.select('img.tonerremain')
            toner = round(int(tag[0]['height']) / self.MAX_IMAGE_HEIGHT * 100)
            attributes = {"friendly_name": "Pozostały toner", "icon": "mdi:flask-outline", "unit_of_measurement": "%", "custom_ui_state_card": "state-card-custom-ui", "templates": {"theme": "if (state < 10) return \'red\'; else return \'default\';"}}
            self.update_sensor('sensor.printer_toner', toner, attributes)

    def update_printer_info_page(self, kwargs):
        self.download_page('http://{}{}'.format(self.HOST, self.INFO_URL))
        if self.page is not None:
            soup = BeautifulSoup(self.page.text, 'html.parser')
            tag = soup.find_all('dd')[4]
            printed_pages = int(tag.string)
            attributes = {"friendly_name": "Wydrukowano", "icon": "mdi:file-document", "unit_of_measurement": "str"}
            self.update_sensor('sensor.printer_printed_pages', printed_pages, attributes)
            tag = soup.find_all('dd')[8]
            drum_usage = 100 - int(tag.string[1:-5])
            attributes = {"friendly_name": "Zużycie bębna", "icon": "mdi:chart-donut", "unit_of_measurement": "%", "custom_ui_state_card": "state-card-custom-ui", "templates": {"theme": "if (state > 90) return \'red\'; else return \'default\';"}}
            self.update_sensor('sensor.printer_drum_usage', drum_usage, attributes)
    def update_sensor(self, entity, state, attributes):
        try:
            self.set_state(entity, state = state, attributes = attributes)
        except:
            return

    def download_page(self, url):
        self.page = None
        try:
            self.page = get(url, timeout = 2)
        except:
            self.error('Host {} unreachable!'.format(self.HOST))
            return
