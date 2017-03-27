#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler, InlineQueryHandler
import ConfigParser

def cmd_start(bot, update):
	chat_id = update.message.chat_id
	text = "Your id used in this chat is "+str(chat_id)
	bot.sendMessage(chat_id, text)

if __name__ == '__main__':
	print "Running discovery ID. CTRL + C to stop"
	config = ConfigParser.RawConfigParser()
	config.read('config.properties')
	token = config.get('Config', 'config.token')
	updater = Updater(token)
	dp = updater.dispatcher
	dp.add_handler(CommandHandler("start", cmd_start))
	updater.start_polling()
	updater.idle()
