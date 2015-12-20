# pznc.py
# insert("ME", "COMSSA", "LOCALHOST", "aedomsan", "m", "2015-07-02", "znc", "THIS IS A FUCKING LONG LOG LINE HEY", "SGP")


import znc, psycopg2, re 
from contextlib2 import closing
from systemd import journal
from datetime import datetime

class pznc(znc.Module):
	description = "PostgreSQL Logger for ZNC"
	
	module_types = [znc.CModInfo.UserModule, znc.CModInfo.NetworkModule]	

	def OnPart(self, user, channel, message):
		journal.send("Channel Parted:" + channel.GetName() )
		return znc.CONTINUE	
	
	def OnChanMsg(self, user, channel, message):
		ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		try:
			self.insert("SAY", channel.GetName(), user.GetHost(), user.GetNick(), self.findMode(channel, user), ts, None, message.s, str(self.GetNetwork()))
		except Exception as e:
			journal.send(repr(e))
		return True

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





## Taken from github
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
		self.insert("TOPIC", channel.GetName(), user.GetHost(), user.GetNick(), None, datetime.now(), None, message.s, str(self.GetNetwork()))
		return True

	def OnQuit(self, user, message, channels):
		for channel in channels:
			self.insert("QUIT", channel.GetName(), user.GetHost(), user.GetNick(), None, datetime.now(), None, message, str(self.GetNetwork()))
		return True

	def OnNick(self, user, new_nick, channels):
		for channel in channels:
			self.insert("NICK", channel.GetName(), user.GetHost(), user.GetNick(), None, datetime.now(), new_nick, None, str(self.GetNetwork()))
		return True

	def OnKick(self, user, target_nick, channel, message):
		self.insert("KICK", channel.GetName(), user.GetHost(), user.GetNick(), None, datetime.now(), target_nick, message, str(self.GetNetwork()))
		return True

	def OnJoin(self, user, channel):
		self.insert("JOIN", channel.GetName(), user.GetHost(), user.GetNick(), None, datetime.now(), None, None, str(self.GetNetwork()))
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
		self.insert("ME", channel.GetName(), user.GetHost(), user.GetNick(), None, datetime.now(), None, message.s, str(self.GetNetwork()))
		return True
