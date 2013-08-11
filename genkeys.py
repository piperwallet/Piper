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
		con = sqlite3.connect('/home/pi/Printer/keys.db3')
		cur = con.cursor()
		cur.execute("SELECT coinType, addrPrefix FROM piper_settings LIMIT 1;")
		row = cur.fetchone()
		coinType = row[0]
		addrPrefix = row[1]
	except sqlite3.Error, e:
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.commit()
			con.close()
		
	if(coinType == "litecoin"):
		process = Popen(["./vanitygen-litecoin", "-q", "-L", "-t","1","-s", "/dev/random", addrPrefix], stdout=PIPE)
	else:
		process = Popen(["./vanitygen", "-q", "-t","1","-s", "/dev/random", addrPrefix], stdout=PIPE)

	results = process.stdout.read()
	addrs = results.split()
	pubkey = addrs[3]
	privkey = addrs[5]
	
#we do a basic length sanity check on the public and private keys
	if len(privkey) == 51 and len(pubkey) >= 27:
		keysAreValid = True
	else:
		keysAreValid = False 

