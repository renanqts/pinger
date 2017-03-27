import MySQLdb as mdb
from datetime import datetime
from time import gmtime, strftime
import sys, logging

class Database (object):

	db = None
	cursor = None

	logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)
	logger = logging.getLogger(__name__)

	def __init__(self, config):
		self.db = mdb.connect(host = config.get('DB', 'DB.host'),
						user = config.get('DB', 'DB.user'),
						passwd = config.get('DB', 'DB.password'), 
						db = config.get('DB', 'DB.database'))
		self.db.autocommit(True)
		self.db.ping(True)	
		self.cursor = self.db.cursor()

	def getHosts(self):
		try:
			self.cursor.execute("SELECT * FROM pinger.host limit 100")
			result = self.cursor.fetchall()
			return result
   		except mdb.Error, e:
  			self.logger.info(e)

  	def getHostByID(self,id):
		try:
			self.cursor.execute("SELECT * FROM pinger.host WHERE id = %s", (id))
			result = self.cursor.fetchone()
			if result:
				return True, result
			else:
				return False, 'NOTFOUND'
   		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'Error'

	def getHostsActive(self):
		try:
			self.cursor.execute("SELECT * FROM pinger.host WHERE status = true")
			return self.cursor.fetchall()
   		except mdb.Error, e:
  			self.logger.info(e)

  	def getHostByIP(self, ip):
  		try:
			self.cursor.execute("SELECT id FROM pinger.host WHERE ip = %s", (ip))
			result = self.cursor.fetchone()
			if result:
				return True, result
			else:
				return False, 'NOTFOUND'
   		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'Error'


  	def findHost(self,string):
		try:
			self.cursor.execute("SELECT * FROM pinger.host WHERE name LIKE %s OR ip LIKE %s", ('%'+string+'%',string))
			return self.cursor.fetchall()
   		except mdb.Error, e:
  			self.logger.info(e)
  				
  	def setHost(self, string):
		try:
			self.cursor.execute("INSERT INTO host (name,ip,status) VALUES (%s, %s, %s)", (string[0],string[1],True))
			self.db.commit()
			return True
		except mdb.Error as e:
			self.logger.info(e)
  			return False

  	def delHost(self, id):
		try:
			self.cursor.execute("DELETE FROM pinger.host WHERE id = %s", (id))
			self.db.commit()			
			if self.cursor.rowcount == 0:
				return False, 'NOTFOUND'
			else:
				return True, ''
		except mdb.Error as e:
			self.logger.info(e)
  			return False, 'ERROR'

  	def setHostEnable(self, string):
  		try:
			self.cursor.execute("UPDATE pinger.host SET status=True WHERE status = False and ip = %s", (string))
			self.db.commit()
			if self.cursor.rowcount == 0:
				return False
			else:
				return True
		except mdb.Error as e:
			self.logger.info(e)
  			return False

  	def setHostDisable(self, string):
  		try:	
			self.cursor.execute("UPDATE pinger.host SET status=False WHERE status = True and ip = %s", (string))
			self.db.commit()	
			if self.cursor.rowcount == 0:
				return False
			else:
				return True
		except mdb.Error as e:
			self.logger.info(e)
  			return False

  	def delHostByIP(self, ip):
  		flag, host_id = self.getHostByIP(ip)
  		if flag:
  			flag, result = self.delAlertByHost(host_id[0])
  			if not flag and result == 'ERROR':
  				return False, 'ERRORALERT'
  			else:
  				flag, result = self.delHost(host_id)
  				if flag:
  					return True, ''
  				else:
  					return False, 'ERRORDELHOST'
  		else:
  			return False, 'NOTFOUND'

  	def getAlertByHost(self,id):
   		try:
			self.cursor.execute("SELECT id FROM pinger.alert WHERE host_id = %s", (id))
			result = self.cursor.fetchone()
			if result:
				return True, result
			else:
				return False, 'NOTFOUND'
   		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'ERROR'

	def getAlert(self):
   		try:
			self.cursor.execute("SELECT * FROM pinger.alert")
			return self.cursor.fetchall()
   		except mdb.Error, e:
  			self.logger.info(e)

  	def getAlertLimit(self):
   		try:
			self.cursor.execute("SELECT host_id,time FROM pinger.alert WHERE sent = true LIMIT 100")
			result = self.cursor.fetchall()
			if result:
				return True, result
			else:
				return False, 'NOTFOUND'
   		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'ERROR'

  	def getAlertSend(self):
   		try:			
			self.cursor.execute("SELECT * FROM pinger.alert WHERE sent = false and seen= 3")
			return self.cursor.fetchall()
   		except mdb.Error, e:
  			self.logger.info(e)
    
	def setAlert(self, host_id):
		try:
			self.cursor.execute("INSERT INTO alert (host_id,time) VALUES (%s, %s)", (host_id,str(datetime.now())))
			self.db.commit()
			return True, ''
		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'ERROR'

	def delAlert(self, id):
		try:
			self.cursor.execute("DELETE FROM pinger.alert WHERE id = %s", (id))
			self.db.commit()
			if self.cursor.rowcount == 0:
				return False, 'NOTPOSSIBLE'
			else:
				return True, ''
		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'ERROR'

  	def delAlertByHost(self, id):
		try:
			self.cursor.execute("DELETE FROM pinger.alert WHERE host_id = %s", (id))
			self.db.commit()
			if self.cursor.rowcount == 0:
				return False, 'NOTPOSSIBLE'
			else:
				return True, ''
		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'ERROR'

	def setSentAlert(self,id):
		try:
			self.cursor.execute("UPDATE pinger.alert SET sent = true WHERE id = %s", (id))
			self.db.commit()
			return True, ''
		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'ERROR'
  
  	def setSeenAlert(self,alert):
		try:
			self.cursor.execute("UPDATE pinger.alert SET seen = %s WHERE id = %s", (alert[4]+1,alert[0]))
			self.db.commit()
			return True, ''
		except mdb.Error, e:
  			self.logger.info(e)
  			return False, 'ERROR'

	def checkUser(self,telegram_id):
		try:
			self.cursor.execute("SELECT level FROM pinger.user WHERE telegram_id= %s ", (telegram_id))
			if self.cursor.rowcount == 0:
				return 0
			else:
				result = self.cursor.fetchone()
				if 1 in result:
					return 1
				elif 2 in result:
					return 2
   		except mdb.Error, e:
  			self.logger.info(e)
  			return 0

  	def getUsers(self):
  		try:
			self.cursor.execute("SELECT * FROM pinger.user limit 100")
			return self.cursor.fetchall()
   		except mdb.Error, e:
  			self.logger.info(e)

  	def setUser(self, string):
		try:
			self.cursor.execute("INSERT INTO user (user,telegram_id,level) VALUES (%s, %s, %s)", (string[0],int(string[1]),string[2]))
			self.db.commit()
			return True
		except mdb.Error as e:
			self.logger.info(e)
  			return False

  	def delUser(self, string):
		try:
			self.cursor.execute("DELETE FROM pinger.user WHERE telegram_id = %s", (string))
			self.db.commit()		
			if self.cursor.rowcount == 0:
				return False
			else:
				return True
		except mdb.Error as e:
			self.logger.info(e)
  			return False