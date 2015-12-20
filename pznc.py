# pznc.py
# Adam Parsons (me@adamparsons.id.au)
# 
# Requires systemd-journal for debugging, I chose this because any sort of debugging or stdout with modpython is 
# absolutely impossible, this should have taken me an hour to code, but took almost two days because of how 
# awful znc's modpython is, and its awesome, descriptive error messages such as "Module Aborted"
# If you don't have or don't want systemd, just remove any line beginning with 'journal.send' and 
# replace it with "pass" if its the sole statement after an except
# 
# If you're new to python, pip, or anything here and don't know what you're doing, as root run (on debian)
# apt-get install python3-pip znc-dev znc-python build-essential 
# pip3 install contextlib2 psycopg2
# After that, edit the database connection details in this file "postgresConnectString()" to reflect yours
# 
# Note: You will not be able to run this script directly, its a python class, not an executable script, so don't bother trying,
# instead it should be placed inside your znc modules directory (I use /usr/lib/znc/)
# and load it inside your IRC client with "/msg *status loadmod pznc"
# Check your syslog or journalctl for errors in configuration
#
# Some of this is directly copied and pasted from a similar module but for mysql, 
# you can compare theirs here: https://github.com/buxxi/znc-mysql/blob/master/sql.py

import znc, psycopg2, re 
from contextlib2 import closing
from systemd import journal
from datetime import datetime

class pznc(znc.Module):
	description = "PostgreSQL Logger for ZNC"
	
	module_types = [znc.CModInfo.UserModule, znc.CModInfo.NetworkModule]	

	def OnPart(self, user, channel, message):
		try:
			self.insert("PART", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), None, message, str(self.GetNetwork()))
		except Exception as e:
			send.journal(repr(e))
		return True	
	
	def OnChanMsg(self, user, channel, message):
		try:
			self.insert("SAY", channel.GetName(), user.GetHost(), user.GetNick(), self.findMode(channel, user), self.timestamp(), None, message.s, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True

	def timestamp(self):
		ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		return ts

	def postgresConnectString(self):
		dbpass = "j3U8sVnq%6^4"
		connstring = "dbname='pznc' user='adam' host='localhost' password='" + dbpass + "'"
		return connstring

	def insert(self, code, channel, host, zuser, user_mode, date, target_user, message, network):
		journal.send("Inserting")
		connstring = self.postgresConnectString()
		try:
			with closing(psycopg2.connect(connstring)) as conn:
				with closing(conn.cursor()) as cursor:
					cmd = "INSERT INTO chanlog (code, network, channel, host, zuser, user_mode, target_user, message, date) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					cursor.execute(cmd, (code, network, channel, host, zuser, user_mode, target_user, message, date))
					cursor.close()
					conn.commit()
		except Exception as e:
			self.PutModule("Could not save {0} to database caused by: {1} {2}".format(code, type(e), str(e)))
			journal.send(repr(e))

### ----- Untested Below ----- ###

	def resolveTarget(self, target):
		target = target.s
		channel = self.GetNetwork().FindChan(target)
		if channel == None:
			return (None, None)
		user = self.GetNetwork().GetIRCNick()
		return (channel, user)

	def findMode(self, channel, user):
		realUser = channel.FindNick(user.GetNick())
		return chr(realUser.GetPermChar())

	def OnTopic(self, user, channel, message):
		try:
			self.insert("TOPIC", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), None, message.s, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True

	def OnQuit(self, user, message, channels):
		try:
			for channel in channels:
				self.insert("QUIT", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), None, message, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))	
		return True

	def OnNick(self, user, new_nick, channels):
		try:
			for channel in channels:
				self.insert("NICK", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), new_nick, None, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True

	def OnKick(self, user, target_nick, channel, message):
		try:
			self.insert("KICK", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), target_nick, message, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True


	def OnJoin(self, user, channel):
		try:
			self.insert("JOIN", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), None, None, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True

	def OnUserAction (self, target, message):
		(channel, user) = self.resolveTarget(target)
		if channel == None:
			return True
		return self.OnChanAction(user, channel, message)

	def OnUserMsg (self, target, message):
		(channel, user) = self.resolveTarget(target)
		if channel == None:
			return True
		return self.OnChanMsg(user, channel, message)

	def OnChanAction(self, user, channel, message):
		try:
			self.insert("ME", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), None, message.s, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True



### ------ Even more untested ------ ####

	def OnMode(self, user, channel, mode, argument, added, noChange):
		mode = chr(mode)
		code = "MODE"
		if mode == "b":
			code = "BAN" if added else "UNBAN"
		else:
			sign = "+" if added else "-"
			argument = "{0}{1} {2}".format(sign, mode, argument)
		try:
			self.insert(code, channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), None, argument, str(self.GetNetwork()))
		except Exception as e:
			journal.self(repr(e))
		return True

	def OnOp(self, user, target_user, channel, noChange):
		try:
			self.insert("OP", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), target_user.GetNick(), None, str(self.GetNetwork()))
		except Exception as e:
			journal.self(repr(e))
		return True

	def OnDeop(self, user, target_user, channel, noChange):
		try:
			self.insert("DEOP", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), target_user.GetNick(), None, str(self.GetNetwork()))
		except Exception as e:
			journal.self(repr(e))
		return True

	def OnVoice(self, user, target_user, channel, noChange):
		try:
			self.insert("VOICE", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), target_user.GetNick(), None, str(self.GetNetwork()))
		except Exception as e:
			journal.self(repr(e))
		return True

	def OnDevoice(self, user, target_user, channel, noChange):
		try:
			self.insert("DEVOICE", channel.GetName(), user.GetHost(), user.GetNick(), None, self.timestamp(), target_user.GetNick(), None, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True

''' This is broken, will break znc, don't know why, don't care at all, if someone feels like fixing it, feel free
	def OnLoad(self, args, message):
		match = re.search("(.*?):(.*?)@(.*)", args)
		if match:
			self.username = match.group(1)
			self.password = match.group(2)
			self.host = match.group(3)
			return True
		else:
			return False
'''