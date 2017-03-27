#coding: utf-8
import ConfigParser, logging, re
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram import Bot
from database import Database

#load configurations
config = ConfigParser.RawConfigParser()
config.read('config.properties')
#database configuration
db = Database(config)
#Log format
logging.basicConfig(format='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def getConfig():
	config = ConfigParser.RawConfigParser()
	config.read('config.properties')

def checkUserWrite(chat_id, bot):
	if 1 == db.checkUser(chat_id):
		return True
	else:
		text = 'I am sorry. You are not authorized :( \n' + \
				'Telegram id chat '+str(chat_id)
		bot.sendMessage(chat_id, text)

def checkUserRead(chat_id, bot):
	result = db.checkUser(chat_id)
	if 1 == result or 2 == result:
		return True
	else:
		text = 'I am sorry. You are not authorized :( \n' + \
			'Telegram id chat '+str(chat_id)
		bot.sendMessage(chat_id, text)

def cmd_start(bot, update):
	chat_id = update.message.chat_id
	logger.info('ID '+str(chat_id))
	if checkUserRead(chat_id,bot):
		text = "Options:\n" + \
		"/start \n" + \
		"/list - List all devices \n" + \
		"/find <devicename> ou <ip/domain> \n" + \
		"/add <name-without-space> <ip/domain>\n" + \
		"/remove <ip/domain>\n" + \
		"/enable <ip/domain>\n" + \
		"/disable <ip/domain>\n" + \
		"/alerts - List all alerts\n" + \
		"/userid - Discovery id-user Telegram\n" + \
		"/userlist \n" + \
		"/useradd <name-without-space> <telegram_id> <level> - Where level is admin or user\n" + \
		"/userdel <telegram_id>"
		bot.sendMessage(chat_id, text)

def error(bot, update, error):
	logger.warn('Update "%s" caused error "%s"' % (update, error))

def cmd_list(bot, update):
	chat_id = update.message.chat_id
	if checkUserRead(chat_id,bot):
		result = db.getHosts()
		if result:
			size = len(result)
			if(size == 1):
				message = 'Host:\n'
				message = result[0][1]+' '+result[0][2]
				if result[0][3] == False:
					message+= ' disable'
				else:
					message+= ' enable'
			if size > 1:
				message = 'List of hosts: \n'
				for row in result:
					message += row[1]+' '+row[2]
					if row[3] == False:
						message+= ' disable \n'
					else:
						message+= ' enable \n'
			message = message.decode('iso-8859-1').encode('utf8')
			bot.sendMessage(chat_id, message)
		else:
			bot.sendMessage(chat_id, text='I am sorry, nothig was found :(')

def cmd_find(bot, update, args):
	chat_id = update.message.chat_id
	if checkUserRead(chat_id,bot):
		if len(args) != 1:
			bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/find <devicename> ou <ip/domain>"')
		else:
			result = db.findHost(args[0])
			if result:
				message = 'Found: \n'
				for row in result:
					message += row[1]+' '+row[2]
					if row[3] == False:
						message+= ' disable \n'
					else:
						message+= ' enable \n'
				message = message.decode('iso-8859-1').encode('utf8')
				bot.sendMessage(chat_id, message)
			else:
				bot.sendMessage(chat_id, text='I am sorry, nothig was found :(')

def cmd_add(bot, update, args):
	chat_id = update.message.chat_id
	if checkUserWrite(chat_id,bot):
		if len(args) != 2:
			bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/add <name-without-space> <ip/domain>"')
		else:
			#regex to get IP/Domain'
			regex = r'^[\w\d_.-]*$'
			if re.match(regex,args[1]):
				if db.setHost(args):
					logger.info('Host %s %s added by %s' % (args[0],args[1],chat_id))
					bot.sendMessage(chat_id, text='Host '+args[0]+' '+args[1]+' added.')
				else:
					bot.sendMessage(chat_id, text='I am sorry, but I could not add. ' + \
						'Check if exist <nome> or <ip/domain> equals.\n' + \
						'You can use: /list or /find')
			else:
				bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/add <name-without-space> <ip/domain>"')

def cmd_remove(bot, update, args):
	chat_id = update.message.chat_id
	if checkUserWrite(chat_id,bot):
		if len(args) != 1:
			bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/remove <ip/dominio>"')
		else:
			#regex to get IP/Domain'
			regex = r'^[\w\d_.-]*$'
			if re.match(regex,args[0]):
				flag, result = db.delHostByIP(args[0])
				if flag:
					logger.info('Host %s removed by %s' % (args[0],chat_id))
					bot.sendMessage(chat_id, text='Device '+args[0]+' removed')
				elif 'NOTFOUND':
					bot.sendMessage(chat_id, text='I am sorry. I could not find <ip/domain>. ')
				elif 'ERRORALERT':
					bot.sendMessage(chat_id, text='I am sorry. I could not remove. ')
				elif 'ERROR':
					bot.sendMessage(chat_id, text='I am sorry. I could not remove. ' + \
						'Check if <ip/domain> is okay.\n' + \
						'You can use: /list or /find')
			else:
				bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/remove <ip/domain>"')

def cmd_enable(bot, update, args):
	chat_id = update.message.chat_id
	if checkUserWrite(chat_id,bot):
		if len(args) != 1:
			bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/enable <ip/domain>"')
		else:
			#regex to get IP/Domain'
			regex = r'^[\w\d_.-]*$'
			if re.match(regex,args[0]):
				if db.setHostEnable(args[0]):
					logger.info('Host: %s enable by %s' % (args[0],chat_id))
					bot.sendMessage(chat_id, text='Device '+args[0]+' enable')
				else:
					bot.sendMessage(chat_id, text='I coud not enable. ' + \
						'Check if <ip/domain> is okay.\n' + \
						'You can use: /list or /find')
			else:
				bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/enable <ip/domain>"')

def cmd_disable(bot, update, args):
	chat_id = update.message.chat_id
	if checkUserWrite(chat_id,bot):
		if len(args) != 1:
			bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/disable <ip/domain>"')
		else:
			#regex to get IP/Domain'
			regex = r'^[\w\d_.-]*$'
			if re.match(regex,args[0]):
				if db.setHostDisable(args[0]):
					logger.info('Host: %s disable by %s' % (args[0],chat_id))
					bot.sendMessage(chat_id, text='Device '+args[0]+' disable')
				else:
					bot.sendMessage(chat_id, text='I coud not disable. ' + \
						'Check if <ip/domain> is okay.\n' + \
						'You can use: /list or /find')
			else:
				bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/disable <ip/domain>"')

def cmd_alerts(bot, update):
	chat_id = update.message.chat_id
	if checkUserRead(chat_id,bot):
		flag, alerts = db.getAlertLimit()
		if flag:
			if len(alerts) == 1:
				flag, host = db.getHostByID(alerts[0][0])
				if flag:
					message = 'Host down:\n'
		            #Convert to UTF8
					message += (host[1]+' '+host[2]+' '+"{:%H:%M %d %b %Y}".format(alerts[0][1])).decode('iso-8859-1').encode('utf8')
					bot.sendMessage(chat_id, message)
				else:
					logger.info('I could not get host %s, error %s' %(str(alerts[0][0]),host))
			else:
				message = 'List of hosts down: \n'
				for alert in alerts:
					flag, host = db.getHostByID(alert[0])
					if flag:
						message += (host[1]+' '+host[2]+' '+"{:%H:%M %d %b %Y}".format(alert[1])+'\n').decode('iso-8859-1').encode('utf8')

					else:
						logger.info('I could not get host %s, error %s' %(str(alert[0]),host))
				bot.sendMessage(chat_id, message)
		else:
			bot.sendMessage(chat_id, text='I am sorry, nothig was found :(')

def cmd_userid (bot, update):
	chat_id = update.message.chat_id
	firstname = update.message.from_user.first_name
	lastname = update.message.from_user.last_name

	message = 'The user '+str(firstname)+' '+str(lastname)+\
		' is trying get access, if you wish accept, ' + \
		'send to me: /useradd <username> '+str(chat_id)+' <level>'

	#send a message with telegram user id to user/group defined in config.properties
	group = config.get('Config', 'config.group')
	bot.sendMessage(chat_id=group, text=message)
	#send a message to the user
	bot.sendMessage(chat_id, text='Request sent.')

def cmd_userlist(bot, update):
	chat_id = update.message.chat_id
	if checkUserWrite(chat_id,bot):
		result = db.getUsers()
		if result:
			message = 'User(s):\n'
			for row in result:
				if 1 == row[3]:
					message += (row[1]+' '+str(row[2])+' admin'+'\n').decode('iso-8859-1').encode('utf8')
				elif 2 == row[3]:
					message += (row[1]+' '+str(row[2])+' user'+'\n').decode('iso-8859-1').encode('utf8')
			bot.sendMessage(chat_id, message)
		else:
			bot.sendMessage(chat_id, text='I could not find users')

def cmd_useradd(bot, update, args):
	chat_id = update.message.chat_id
	if checkUserWrite(chat_id,bot):
		if len(args) != 3:
			bot.sendMessage(chat_id, text='I could not understand you! \nUse: ' + \
				'"/useradd <name-without-space> <telegram_id> <level> - Where level is admin or user"')
		else:
			#regex to get natural numbers'
			regex_telegram_id = r'^[-]?[0-9][0-9]*$'
			if re.match(regex_telegram_id,args[1]) and args[2] in {'admin','user'}:
				if 'admin' in args[2] :
					args[2] = 1
				elif 'user' in args[2]:
					args[2] = 2
				if db.setUser(args):
					logger.info('User %s %s %s addded by %s' % (args[0], args[1], args[2], chat_id))
					bot.sendMessage(chat_id, text='User '+args[0]+' '+args[1]+' added')
				else:
					bot.sendMessage(chat_id, text='I am sorry. I could not add. ' + \
						'Check if <telegram_id> is okay.\n' + \
						'You can use: /userlist')
			else:
				bot.sendMessage(chat_id, text='I could not understand you! \nUse: ' + \
					'"/useradd <name-without-space> <telegram_id> <level> - Where level is admin or user"')

def cmd_userdel(bot, update, args):
	chat_id = update.message.chat_id
	if checkUserWrite(chat_id,bot):
		if len(args) != 1:
			bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/userdel <telegram_id>"')
		else:
			#regex to get natural numbers'
			regex = r'^[-]?[0-9][0-9]*$'
			if re.match(regex,args[0]):
				if db.delUser(args[0]):
					logger.info('User %s removed by %s' % (args[0], chat_id))
					bot.sendMessage(chat_id, text='User '+args[0]+' removed')
				else:
					bot.sendMessage(chat_id, text='I am sorry. I could not remove. ' + \
						'Check if <telegram_id> is okay.\n' + \
						'You can use: /userlist')
			else:
				bot.sendMessage(chat_id, text='I could not understand you! \nUse: "/userdel <telegram_id>"')

def main():
	logger.info('Starting...')
	#Load token
	token = config.get('Config', 'config.token')
	updater = Updater(token)
	b = Bot(token)
	logger.info("BotName: <%s>" % (b.name))

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("start", cmd_start))
	dp.add_handler(CommandHandler("list", cmd_list))
	dp.add_handler(CommandHandler("find", cmd_find, pass_args = True))
	dp.add_handler(CommandHandler("add", cmd_add, pass_args = True))
	dp.add_handler(CommandHandler("remove", cmd_remove, pass_args = True))
	dp.add_handler(CommandHandler("enable", cmd_enable, pass_args = True))
	dp.add_handler(CommandHandler("disable", cmd_disable, pass_args = True))
	dp.add_handler(CommandHandler("alerts", cmd_alerts))
	dp.add_handler(CommandHandler("userid", cmd_userid))
	dp.add_handler(CommandHandler("userlist", cmd_userlist))
	dp.add_handler(CommandHandler("useradd", cmd_useradd, pass_args = True))
	dp.add_handler(CommandHandler("userdel", cmd_userdel, pass_args = True))

	# Start the Bot
	updater.start_polling()

 	logger.info('Started!')
	# Block until the you presses Ctrl-C or the process receives SIGINT,
	# SIGTERM or SIGABRT. This should be used most of the time, since
	# start_polling() is non-blocking and will stop the bot gracefully.
	updater.idle()

if __name__ == '__main__':
	main()
