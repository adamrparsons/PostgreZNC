# pznc.py

import znc, psycopg2, re
from contextlib2 import closing
from systemd import journal

class pznc(znc.Module):
	description = "PostgreSQL Logger for ZNC"
	
	module_types = [znc.CModInfo.UserModule, znc.CModInfo.NetworkModule]	

	

	def postgresConnectString():
		dbpass = j3U8sVnq%6^4
		connstring = "dbname='pznc' user='adam' host='localhost' password='" + dbpass + "'"
		return connstring

	def insert(self, code, channel, host, user, user_mode, date, target_user, message, network):
		journal.send("Inserting")
		connstring = postgresConnectString()
		try:
			with closing(psycopg2.connect(connstring)) as conn:
				with closing(conn.cursor()) as cursor:
					cmd = "INSERT INTO chanlog values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
					cursor.execute(cmd, host, zuser, user_mode, date.isoformat(), target_user, message, network,)
					cur.close()
					conn.commit()
		except Exception as e:
			self.PutModule("Could not save {0} to database caused by: {1} {2}".format(code, type(e), str(e)))
