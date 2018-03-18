import appdaemon.appapi as appapi
from bs4 import BeautifulSoup
from requests import get
from datetime import datetime

class BrotherPrinterStatus(appapi.AppDaemon):

	def initialize(self):

		self.MAX_IMAGE_HEIGHT = 60
		self.INFO_URL = '/general/information.html'
		self.STATUS_URL = '/general/status.html'

		try:
			if self.args['host'] is not None:
				self.HOST = self.args['host']
		except KeyError:
			self.error('Wrong arguments! You must supply a valid printer hostname or IP address.')
			return
		if 'interval' in self.args:
			interval = int(self.args['interval'])
		else:
			interval = 10
		self.run_every(self.update_printer_status_page, datetime.now(), interval)
		self.run_every(self.update_printer_info_page, datetime.now(), 5 * 60)

	def update_printer_status_page(self, kwargs):
		self.download_page('http://{}{}'.format(self.HOST, self.STATUS_URL))
		if self.page is not None:
			soup = BeautifulSoup(self.page.text, 'html.parser')
			tag = soup.find_all('dd')[0]
			status = tag.string
			attributes = {"friendly_name": "Status drukarki", "icon": "mdi:printer"}
			self.update_sensor('sensor.printer_status', status, attributes)
			tag = soup.select('img.tonerremain')
			toner = round(int(tag[0]['height']) / self.MAX_IMAGE_HEIGHT * 100)
			attributes = {"friendly_name": "Pozostały toner", "icon": "mdi:flask-outline", "unit_of_measurement": "%"}
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
			attributes = {"friendly_name": "Zużycie bębna", "icon": "mdi:chart-donut", "unit_of_measurement": "%"}
			self.update_sensor('sensor.printer_drum_usage', drum_usage, attributes)

	def update_sensor(self, entity, state, attributes):
		try:
			self.set_state(entity, state = state, attributes = attributes)
		except:
			return

	def download_page(self, url):
		self.page = None
		try:
			self.page = get(url)
		except:
			self.error('Host unreachable!')
			return
