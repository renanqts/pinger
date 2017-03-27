#coding: utf-8
from database import Database
from telegram import Bot
import logging

class Alert (object):
	
	db = None
	config = None

	logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)
	logger = logging.getLogger(__name__)

	def __init__(self, db, config):
		self.db = db
		self.config = config

	def sendMessage(self, message):
		#Send messages by Bot

		try:
			#Load the telegram bot
			token = self.config.get('Config', 'config.token')
			bot = Bot(token)
			#send message
			group = self.config.get('Config', 'config.group')
			bot.sendMessage(chat_id=group, text=message)
			return True
		except Exception, e:
			self.logger.info(e)
			return False

	def formatMsgHostsUp(self, alerts):
		#Only one alert
		if len(alerts)==1:
			flag, host = self.db.getHostByID(alerts[0][1])
			if flag:
				message = 'I noticed that the host is up:\n'
				message += host[1]+' '+host[2]
			else:
				self.logger.info('I could not get the host %s' %(str(alerts[0][1])))	
		else:
			message = 'I noticed that the hosts are up: \n'
			for alert in alerts:
				flag, host = self.db.getHostByID(alert[1])
				if flag:
					message +=host[1]+' '+host[2]+'\n'
				else:
					self.logger.info('I could not get the host %s, error %s' %(str(alert[1]),host))
		return message

	def execDelAlerts(self, alerts):
		#Compare with alert was sent
		#If was, send message that the host is up
		#If wasn't, remove old alert

		#remove old alerts that was not sent
		for alert in alerts:
			if alert[3] == False:
				flag, result = self.db.delAlert(alert[0])
				if not flag:
					self.logger.info('I could not remove the alert %s, error %s' % (alert[0],result))
				alerts.remove(alert)
		
		if alerts:
			#format alerts to send as UP
			message = self.formatMsgHostsUp(alerts)
			if message:
				if not self.sendMessage(message):
					self.logger.info('I could not send message hosts up')
				else:
					#delete alerts that was sent by message
					for alert in alerts:
						flag, result = self.db.delAlert(alert[0])
						if not flag:
							self.logger.info('Nao foi possivel deletar o alerta %s, error %s' % (str(alert[0]),result))
			else:
				self.logger.info('Nao foi possivel formatar a mensagem de hosts up')			

	def setAlerts(self, hosts):
		#Insert array alerts

		for host in hosts:
			flag, result = self.db.setAlert(host[0])
			if not flag:
				self.logger.info('I could not insert alert to host %s, erro %s' % (str(host[0]),result))

	def formatMsgHostsDown(self, alerts):

		#Only one alert
		if(len(alerts)==1):
			#get host by alert
			flag, host = self.db.getHostByID(alerts[0][1])
			if flag:
				message = 'I noticed that the host is down:\n'
				message += host[1]+' '+host[2]
			else:
				self.logger.info('I could not get the host %s' %(str(alerts[0][1])))
		else:
			message = 'I noticed that the hosts are down: \n'
			for alert in alerts:
				#get host by alert
				flag, host = self.db.getHostByID(alert[1])
				if flag:
					message +=host[1]+' '+host[2]+'\n'
				else:
					self.logger.info('I could not get the host %s, error %s' %(str(alert[1]),host))
		return message

	def execSendDown(self, alerts):
		#Format and execute send of alerts

		#Formatting message hosts down
		message = self.formatMsgHostsDown(alerts)
		if message:
			#try send message with hosts down
			if self.sendMessage(message):
				#update alerts with status sent
				for alert in alerts:
					flag, result = self.db.setSentAlert(alert[0])
					if not flag:
						self.logger.info('I could not update alert with status sent %s, error %s' % (str(alert[0]),result))
			else:
				self.logger.info('I could not send message with alerts down')

	def procAlerts(self, new_alerts):
		#All of process of comparation is done here
		#compare old alerts with new alert and identify if the alert was seen by 3 times
		#if alert was seen by 3 times, it will be sent as message

		#if exist, get alerts
		old_alerts = self.db.getAlert()

		#check if new alerts was found
		if new_alerts:
			#Check if exist old alerts to compare with new alerts
			if old_alerts:
				#cast to list
				old_alerts = list(old_alerts)
				#compare new alerts with old alerts to find recurrence
				for new_alert in new_alerts:
					found = False
					for old_alert in old_alerts:
						if new_alert[0] == old_alert[1]:
							#Check if alert was seen to 3 times.
							#If was, don't increment
							#If wasn't, incrise the count 
							if old_alert[4] < 3:
								flag, result = self.db.setSeenAlert(old_alert)
								if not flag:
									self.logger.info('I could not update alert count %s, erro %s' % (str(old_alert[0]),result))
							#decrease list of comparison because the element was found
							old_alerts.remove(old_alert)
							found = True

					#It is a new alert and must to insert in table
					if not found:
						flag, result = self.db.setAlert(new_alert[0])
						if not flag:
							self.logger.info('I could not insert alert to host %s, erro %s' % (str(new_alert[0]),result))
				if old_alerts:
					#The comparation was finished and there are old alerts to remove
					self.execDelAlerts(old_alerts)
			else:
				#Insert all alerts found
				self.setAlerts(new_alerts)
		elif old_alerts:
			#if wasn't found new alerts in test ICMP, remove all old alerts
			self.execDelAlerts(old_alerts)

		#All list of alerts was updated, 
		alerts = self.db.getAlertSend()
		if alerts:
			self.execSendDown(alerts)
