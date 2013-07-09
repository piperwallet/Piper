#!/usr/bin/python
import Image
import ImageDraw
import ImageFont
import qrcode
import sys
from Adafruit_Thermal import *

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


#open serial number file which tracks the serial number
snumfile = open('serialnumber.txt', 'r+')
snum = snumfile.read()

#open the printer itself
printer = Adafruit_Thermal("/dev/ttyAMA0", 19200, timeout=5)


#load a blank image of the paper wallet with no QR codes or keys on it which we will draw on
finalImg = Image.open("btc-wallet-blank.bmp")

#this actually generates the keys.  see the file genkeys.py or genkeys_forget.py
import genkeys as btckeys 

if btckeys.keysAreValid == False:
	printer.write("Error: The generated keys (public/private) are not the correct length.  Please try again.")

if rememberKeys == True:
	f = open("keys.txt", 'a+')
	f.write("Public Key: "+btckeys.pubkey)
	f.write("\nPrivate Key: "+btckeys.privkey)
	f.write("\n---------------------------------\n")
	f.close()



#---begin the public key qr code generation and drawing section---

#we begin the QR code creation process
#feel free to change the error correct level as you see fit
qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_M,
    box_size=10,
    border=0,
)

qr.add_data(btckeys.pubkey)
qr.make(fit=True)

pubkeyImg = qr.make_image()

#resize the qr code to match our design
pubkeyImg = pubkeyImg.resize((175,175), Image.NEAREST)


font = ImageFont.truetype("/home/pi/ubuntu-font-family-0.80/UbuntuMono-R.ttf", 20)
draw = ImageDraw.Draw(finalImg)


startPos=(110,38)
charDist=15
lineHeight=23
lastCharPos=0

keyLength = len(btckeys.pubkey)

#draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
for x in range(0,keyLength/17):
	lastCharPos=0
	#print a line
	for y in range(0, 17):
		theChar = btckeys.pubkey[(x*17)+y]
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
qr.add_data(btckeys.privkey)
qr.make(fit=True)

privkeyImg = qr.make_image()

#resize the qr code to match our design
privkeyImg = privkeyImg.resize((220,220), Image.NEAREST)


startPos=(110,807)
charDist=15
lineHeight=23
lastCharPos=0

keyLength = len(btckeys.privkey)

#draw 2 lines of 17 characters each.  keyLength always == 34 so keylength/17 == 2
for x in range(0,keyLength/17):
	lastCharPos=0
	#print a line
	for y in range(0, 17):
		theChar = btckeys.privkey[(x*17)+y]
		charSize = draw.textsize(theChar, font=font)
		#print charSize
		if y == 0:
			draw.text((startPos[0],startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
			lastCharPos = startPos[0]+charSize[0]+(charDist-charSize[0])
		else:
			draw.text((lastCharPos,startPos[1]+(lineHeight*x)),theChar, font=font, fill=(0,0,0))
			lastCharPos = lastCharPos + charSize[0] + (charDist-charSize[0])


#draw the QR code on the final image
finalImg.paste(privkeyImg, (125, 560))

#---end the private key qr code generation and drawing section---



#create the divider
leftMarkText = "Serial Number: "+snum
rightMarkText = "Piperwallet.com"

leftMarkSize = draw.textsize(leftMarkText, font=font)
rightMarkSize = draw.textsize(rightMarkText, font=font)

leftMarkOrigin = (10, 10)
rightMarkOrigin = (384-rightMarkSize[0]-10, 10)


dividerLineImg = Image.open("dividerline.bmp")
font = ImageFont.truetype("/home/pi/Helvetica.ttf", 20)
draw = ImageDraw.Draw(dividerLineImg)

draw.text(leftMarkOrigin, leftMarkText, font=font, fill=(255,255,255))
draw.text(rightMarkOrigin,rightMarkText, font=font, fill=(255,255,255))





#do the actual printing
for x in range(0, numCopies):

	printer.printImage(finalImg)

	printer.printChar(btckeys.privkey[:17]+"\n")
	printer.justify('R')
	printer.printChar(btckeys.privkey[17:34]+"\n")
	printer.justify('L')
	printer.printChar(btckeys.privkey[34:]+"\n")

	#print the divider line
	printer.printImage(dividerLineImg)
	
	#print some blank space so we can get a clean tear of the paper
	time.sleep(0.3)
	printer.feed(1)
	time.sleep(0.3)
	printer.feed(1)
	time.sleep(0.3)
	printer.feed(1)





printer.sleep()      # Tell printer to sleep
printer.wake()       # Call wake() before printing again, even if reset
printer.setDefault() # Restore printer to defaults

#update serial number
snumfile.seek(0,0)
snumfile.write(str(int(snum)+1))
snumfile.close()
