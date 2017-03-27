About:

The project was thought to monitor devices. If you need a simple way to monitor your devices by cell phone, you can use that.
With Pinger (name of project), you can receive alerts about the status of devices and manage them by Telegram.

Requirements:

Linux + MariaDB + Python

What I used:

- Raspberry PI 3
- Raspbian
- MariaDB
- Python 2.7
- Python-telegram-bot

How it works:

The Pinger runs in two modules.

- Listener Telegram Bot:

This script was create using the Python-telegram-bot module to provide an interface with Telegram. 
To use this interface, you need to create a Bot in Telegram API, than, you have to configure this Bot token inside the file config.properties. If you don't know how create Bot in Telegram, go to this page: https://core.telegram.org/bots

To access the interface by Bot, you have to create the first user in database, for it, you can use the script 'useradd.py'. Others users can be created using the interaction with the Bot.
The users have two levels of permissions:
	-User, in this level you can use only read functions;
	-Admin, you can use all functions.

- Script monitor ICMP

This scripts is responsible to monitor all hosts in database using ping (ICMP). If it notice that some host is down or up, it send a message to user or group configured in config.properties.

Installation:

Install Raspbian (Or other OS as you wish) in Raspbian and than, run: 
apt-get install mariadb-server python-dev python-pip python-mysqldb

pip install python-telegram-bot

Configuration:

- Run chmod +x adduser.py discoveryid.py
- Create the database structure like in scriptdb. Don't forget to change the 'Password DB' to your password database.
- Configure the config.properties to your enviroment.
- You must create the BOT in Telegram API;
- To discovery your telegram id, put your Bot token in config.properties and than, run the script discoveryid.py. After than, send /start to your BOT, it will answer you. Put the telegram id in config.properties too.
- To create the first user, run adduser.py

Starting the Pinger:

After all configurations, you can test Pinger running the scripts:

python pinger.py
python listener.py

In my case, I put the lines below in /etc/rc.local to start with the system.

/usr/bin/python /var/scripts/pinger/pinger.py > /dev/null 2> /var/scripts/pinger/log/pinger.log
/usr/bin/python /var/scripts/pinger/listener.py > /dev/null 2> /var/scripts/pinger/log/listener.log

Feel free to choose the paths and ways to run the scripts.
