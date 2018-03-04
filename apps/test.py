import appdaemon.appapi as appapi

class TestLog(appapi.AppDaemon):

  def initialize(self):

    self.log('test')
