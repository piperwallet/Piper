# This file is part of Piper.
#
#    Piper is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Piper is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Piper.  If not, see <http://www.gnu.org/licenses/>.
#
# Piper Copyright (C) 2013  Christopher Cassano

import os
from subprocess import Popen, PIPE
import sqlite3

pubkey = ""
privkey = ""
keysAreValid = False

def genKeys():
	global pubkey, privkey, keysAreValid

	keysAreValid = False


	con = None
	try:
		con = sqlite3.connect('/home/pi/Printer/settings.db3')
		cur = con.cursor()
		cur.execute("SELECT CoinFormats.versionNum FROM Settings, CoinFormats WHERE Settings.key='cointype' and Settings.value = CoinFormats.name;")
		row = cur.fetchone()
		versionNum = str(row[0])

		cur.execute("SELECT value FROM Settings WHERE key='addrPrefix';");
		row = cur.fetchone()
		addrPrefix = row[0]
		
	except sqlite3.Error, e:
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.commit()
			con.close()
		
	process = Popen(["./vanitygen", "-q", "-t","1","-s", "/dev/random","-X", versionNum, addrPrefix], stdout=PIPE)

	results = process.stdout.read()
	addrs = results.split()
	pubkey = addrs[3]
	privkey = addrs[5]
	

