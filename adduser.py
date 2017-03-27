#!/usr/bin/env python

def insertUser(args):
  #load modules
  from database import Database
  import ConfigParser

  #load configurations
  config = ConfigParser.RawConfigParser()
  config.read('config.properties')
  #database configuration
  db = Database(config)

  #add user
  if db.setUser(args):
    print "\n Added!"
  else:
    print "\n I couldn't add!"

if __name__ == '__main__':
  ans=True
  while ans:
      print ("""
      1.Add commun user (Only read options)
      2.Add admin user
      3.Exit/Quit
      """)
      ans=raw_input("What would you like to do? ") 
      if ans=="1":
        args = []
        name = raw_input("Name: ")
        args.append(name)
        id = raw_input("Telegram id: ")
        args.append(id)
        args.append(2)
        insertUser(args)
      elif ans=="2":
        args = []
        name = raw_input("Name: ")
        args.append(name)
        id = raw_input("Telegram id: ")
        args.append(id)
        args.append(1)
        insertUser(args)
      elif ans=="3":
        print("\n Goodbye :D\n")
        ans = None 
      elif ans !="":
        print("\n Not valid choice try again") 