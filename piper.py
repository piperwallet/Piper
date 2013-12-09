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
import sqlite3
from Adafruit_Thermal import *


def print_seed(seed):

	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)


	printer.println(seed)
	
	printer.feed(3)


	printer.sleep()      # Tell printer to sleep
	printer.wake()       # Call wake() before printing again, even if reset
	printer.setDefault() # Restore printer to defaults



def print_keypair(pubkey, privkey, leftBorderText):

#open the printer itself
	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)

#check the cointype to decide which background to use
	con = None
	try:
		con = sqlite3.connect('/home/pi/Printer/keys.db3')
		cur = con.cursor()
		cur.execute("SELECT coinType FROM piper_settings LIMIT 1;")
		row = cur.fetchone()
		coinType = row[0]
	except sqlite3.Error, e:
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.commit()
			con.close()
		
	if(coinType == "litecoin"):
		finalImgName="ltc-wallet"
	else:
		finalImgName="btc-wallet"


#load a blank image of the paper wallet with no QR codes or keys on it which we will draw on
	if(len(privkey) <= 51):
		finalImgName += "-blank.bmp"
	else:
		finalImgName += "-enc.bmp"

	finalImgFolder = "/home/pi/Printer/Images/"
	finalImg = Image.open(finalImgFolder+finalImgName)



#---begin the public key qr code generation and drawing section---

#we begin the QR code creation process
#feel free to change the error correct level as you see fit
	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_M,
	    box_size=10,
	    border=0,
	)

	qr.add_data(pubkey)
	qr.make(fit=True)

	pubkeyImg = qr.make_image()

#resize the qr code to match our design
	pubkeyImg = pubkeyImg.resize((175,175), Image.NEAREST)


	font = ImageFont.truetype("/usr/share/fonts/ttf/ubuntu-font-family-0.80/UbuntuMono-R.ttf", 20)
	draw = ImageDraw.Draw(finalImg)


	startPos=(110,38)
	charDist=15
	lineHeight=23
	lastCharPos=0

	keyLength = len(pubkey)

	while(keyLength % 17 != 0):
		pubkey += " "
		keyLength = len(pubkey)




#draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
	for x in range(0,keyLength/17):
		lastCharPos=0
		#print a line
		for y in range(0, 17):
			theChar = pubkey[(x*17)+y]
			charSize = draw.textsize(theChar, font=font)
			
			#if y is 0 then this is the first run of this loop, and we should use startPos[0] for the x coordinate instead of the lastCharPos
			if y == 0:
				draw.text((startPos[0],startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = startPos[0]+charSize[0]+(charDist-charSize[0])
			else:
				draw.text((lastCharPos,startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = lastCharPos + charSize[0] + (charDist-charSize[0])



#draw the QR code on the final image
	finalImg.paste(pubkeyImg, (150, 106))

#---end the public key qr code generation and drawing section---





#---begin the private key qr code generation and drawing section---

#we begin the QR code creation process
#feel free to change the error correct level as you see fit
	qr = qrcode.QRCode(
	    version=None,
	    error_correction=qrcode.constants.ERROR_CORRECT_M,
	    box_size=10,
	    border=0,
	)
	qr.add_data(privkey)
	qr.make(fit=True)

	privkeyImg = qr.make_image()

#resize the qr code to match our design
	privkeyImg = privkeyImg.resize((220,220), Image.NEAREST)

	#draw the QR code on the final image
	finalImg.paste(privkeyImg, (125, 560))


	startPos=(110,807)
	charDist=15
	lineHeight=23
	lastCharPos=0

	keyLength = len(privkey)

	while(keyLength % 17 != 0):
		privkey += " "
		keyLength = len(privkey)


#draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
	for x in range(0,keyLength/17):
		lastCharPos=0
		#print a line
		for y in range(0, 17):
			theChar = privkey[(x*17)+y]
			charSize = draw.textsize(theChar, font=font)
			#print charSize
			if y == 0:
				draw.text((startPos[0],startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = startPos[0]+charSize[0]+(charDist-charSize[0])
			else:
				draw.text((lastCharPos,startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
				lastCharPos = lastCharPos + charSize[0] + (charDist-charSize[0])

#---end the private key qr code generation and drawing section---



#create the divider
	rightMarkText = "Piperwallet.com"


	font = ImageFont.truetype("/usr/share/fonts/ttf/swansea.ttf", 20)

	rightMarkSize = draw.textsize(rightMarkText, font=font)

	leftMarkOrigin = (10, 15)
	rightMarkOrigin = (384-rightMarkSize[0]-10, 15)

	dividerLineImg = Image.open("/home/pi/Printer/dividerline.bmp")
    
	draw = ImageDraw.Draw(dividerLineImg)    
	draw.text(leftMarkOrigin, leftBorderText, font=font, fill=(0,0,0))
	draw.text(rightMarkOrigin,rightMarkText, font=font, fill=(0,0,0))





    #do the actual printing

	printer.printImage(finalImg, True)
	
	if(len(privkey) <= 51):
		printer.printChar(privkey[:17]+"\n")
		printer.justify('R')
		printer.printChar(privkey[17:34]+"\n")
		printer.justify('L')
		printer.printChar(privkey[34:]+"\n")
	else:
		printer.println(privkey)

	#print the divider line
	printer.printImage(dividerLineImg)
	
	#print some blank space so we can get a clean tear of the paper
	printer.feed(3)





	printer.sleep()      # Tell printer to sleep
	printer.wake()       # Call wake() before printing again, even if reset
	printer.setDefault() # Restore printer to defaults
	
	
	


def genAndPrintKeys(remPubKey, remPrivKey, numCopies, password):


	#open serial number file which tracks the serial number
	snumfile = open('serialnumber.txt', 'r+')
	snum = snumfile.read()

	#open the printer itself
	printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)



	#this actually generates the keys.  see the file genkeys.py or genkeys_forget.py
	import genkeys as btckeys

	btckeys.genKeys()

	if btckeys.keysAreValid == False:
		printer.write("Error: The generated keys (public/private) are not the correct length.  Please try again.")
		
	import wallet_enc as WalletEnc
	#encrypt the keys if needed
	if(password != ""):
		privkey = WalletEnc.pw_encode(btckeys.pubkey, btckeys.privkey, password)
	else:
		privkey = btckeys.privkey
	
	
	rememberKeys = False
	sqlitePubKey = ""
	sqlitePrivKey = ""
	strToWrite = ""
	if remPubKey:
		strToWrite = "\nPublic Key: "+btckeys.pubkey
		sqlitePubKey = btckeys.pubkey
		rememberKeys = True

	if remPrivKey:
		strToWrite = strToWrite + "\nPrivate Key: "+privkey
		sqlitePrivKey = privkey
		rememberKeys = True


	if rememberKeys == True:
		#store it to the sqlite db
		con = None
		try:
			con = sqlite3.connect('/home/pi/Printer/keys.db3')
		        con.execute("INSERT INTO keys (serialnum, public, private) VALUES (?,?,?)", (snum, sqlitePubKey, sqlitePrivKey))
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
		finally:
			if con:
				con.commit()
				con.close()
			
		
		#store it in a flat file on the sd card
		f = open("/boot/keys.txt", 'a+')
		strToWrite = "Serial Number: " + snum + strToWrite
		f.write(strToWrite);
		f.write("\n---------------------------------\n")
		f.close()


	leftMarkText = "Serial Number: "+snum

	#do the actual printing
	for x in range(0, numCopies):

		#piper.print_keypair(pubkey, privkey, leftBorderText)
		print_keypair(btckeys.pubkey, privkey, leftMarkText)
		
		if numCopies > 1 and x < numCopies-1:
			time.sleep(30)




	#update serial number
	snumfile.seek(0,0)
	snumfile.write(str(int(snum)+1))
	snumfile.close()
