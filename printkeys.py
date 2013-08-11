#!/usr/bin/python

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

import Image
import ImageDraw
import ImageFont
import qrcode
import sys
from Adafruit_Thermal import *
import piper as Piper

#define function to print usage and exit
def printUsageAndExit():
	print "Usage: printkeys.py [-r | -f] [numCopies]"
	print "Options explained: "
	print "\t[-r | -f]\tSelect -r or -f to remember or forget the generated keys, respectively.";
	print "\t[numCopies]\tThe number of copies of the paper wallet that you want to print.  A value of 1 would print 1 paper wallet, A value of 4 would print 4 identical paper wallets, etc."
	sys.exit(0)


#check for proper number of arguments
if len(sys.argv) != 3:
	printUsageAndExit()

#check for remember or forget flag
if sys.argv[1] == "-r":
	rememberKeys = True
elif sys.argv[1] == "-f":
	rememberKeys = False
else:
	printUsageAndExit()


#try to parse the number of copies
try:
	numCopies = int(sys.argv[2])
except ValueError:
	printUsageAndExit()

#make sure the number of copies to print is valid
if numCopies <= 0:
	print "The number of copies must be >= 0"
	sys.exit(0);


Piper.genAndPrintKeys(rememberKeys, rememberKeys, numCopies, "")
