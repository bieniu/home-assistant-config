import requests
from bs4 import BeautifulSoup

class BrotherPrinterStatus(appapi.AppDaemon):

	def initialize(self):
		if self.args['host']) is not None:
			host = self.args['host'])
		else:
			raise Exception('Wrong arguments! Argument host must contain IP or hostname of the printer.')