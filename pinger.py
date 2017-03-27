#coding: utf-8
import ConfigParser, logging, time
from database import Database
from ping import Ping
from alert import Alert

from threading import Thread

logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def testICMP(config):

  db = Database(config)
  alert = Alert(db,config)
  ping = Ping()
  ping.thread_count = int(config.get('Config', 'config.numthreads'))

  while True:
    
    logger.info("Start test ICMP: %s" % time.ctime())

    #Get hots
    hosts = list(db.getHostsActive())
    if hosts:
      #test hosts
      tests = list(ping.start(list(hosts)))
      #Process old alerts with new alerts and send messages
      alert.procAlerts(tests)
    else:
      #Check if exist alerts when database is empty. If exist, clean all.
      flag, alerts = db.getAlert()
      if flag:
        for alert in alerts:
            flag, result = self.db.delAlert(alert[0])
            if not flag:
              self.logger.info('I could not delete alerts %s, error %s' % (str(alert[0]),result))
      else:
        self.logger.info('I could not get alerts: %s' % (alerts))
    
    #Uncomment to sleep a while
    #time.sleep( 30 )
    logger.info("End test ICMP: %s" % time.ctime())

if __name__ == '__main__':
  logger.info('Starting...')
  #Load configuration at config.properties
  config = ConfigParser.RawConfigParser()
  config.read('config.properties')
  #Start module ICMP test
  testICMP(config)