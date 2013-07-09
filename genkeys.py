import os
from subprocess import Popen, PIPE



process = Popen(["./vanitygen", "-q", "-t 1", "1"], stdout=PIPE)

results = process.stdout.read()
addrs = results.split()
pubkey = addrs[3]
privkey = addrs[5]
	
#we do a basic length sanity check on the public and private keys
keysAreValid = False
if len(privkey) == 51 and len(pubkey) == 34:
	keysAreValid = True
else:
	keysAreValid = False 

