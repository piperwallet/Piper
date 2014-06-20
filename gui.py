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

import Tkinter as tk
import ttk
import sqlite3
import sys
import piper as Piper
import wallet_enc
import Image
import ImageFont
import ImageDraw
import qrcode
import time
import os
from subprocess import Popen, PIPE
import hdm as HDMWallet

class PiperUtil:
	def reprintPassword(self, event):
		print event.widget.serialnum
		Piper.print_password("Serial Number: "+str(event.widget.serialnum), event.widget.password)


	def splitAndPrint(self, ttp, k, n):
		Piper.splitAndPrint(ttp, k, n)

	def printAsText(self, ttp):
		print "Printing as text: "+ttp
		Piper.printText(ttp);
	
	def printAsQR(self, ttp):
		print "Printing as QR code: "+ttp
		Piper.encodeQRAndPrint(ttp);

	def printBulkWallet(self):
		global tab2
		try:
			qty = int(tab2.bulkQuantity.get())
			for x in range(0,qty):
				self.printWallet()
				if qty > 1 and x < qty-1:
					time.sleep(30)
		
		except ValueError:
			print "Please enter an int!!"
			qrPopup = QRPopup()
			qrPopup.showAlert("Error, enter an integer for the number of wallets field!")
			raise
	
	
	def printWallet(self):
		print "printWallet!"
		global tab1
		try:
			qty = int(tab1.walletQuantity.get())
			
			if(tab1.verPass.get() != tab1.walletPass.get()):
				print "Error, passwords don't match!"
				qrPopup = QRPopup()
				qrPopup.showAlert("Error, passwords don't match!")
				return
			
			remFlag = ""
			
			rKey = tab1.remKey.get()
			if(rKey == 1):
				remFlag = True
			elif(rKey == 2):
				remFlag = False
			else:
				#invalid option, return
				return
			
			remPrivFlag = ""
			rKey = tab1.remPrivKey.get()
			if(rKey == 1):
				remPrivFlag = True
			elif(rKey == 2):
				remPrivFlag = False
			else:
				#invalid option, return
				return
	
			remPWKey = tab1.remPW.get()
			if(remPWKey == 1):
				remPW = True
			elif(remPWKey == 2):
				remPW = False
			else:
				#invalid option, return
				return

			#get cointype
			con = None
			try:
				con = sqlite3.connect('/home/pi/Printer/settings.db3')
				cur = con.cursor()
				cur.execute("SELECT value FROM Settings WHERE Settings.key='cointype';")
				row = cur.fetchone()
				coinType = row[0]
				cur.execute("SELECT value FROM Settings WHERE Settings.key='randomPasswordLength';")
				row = cur.fetchone()
				randPwLength = row[0]
				cur.execute("SELECT value FROM Settings WHERE Settings.key='keyGenType';")
				row = cur.fetchone()
				keyGenType = row[0]

			except sqlite3.Error, e:
				print("Error %s:" % e.args[0])
				sys.exit(1)
			finally:
				if con:
					con.commit()
					con.close()

	
			encKey = tab1.encKey.get()
			if(encKey == 3):
				#generate random password now
				pw = Piper.getRandPass(int(randPwLength))
				tab1.walletPass.set(pw)
				tab1.verPass.set(pw)

			
				
			printPW = tab1.printPW.get()
			if(printPW == 1):
				Piper.genAndPrintKeysAndPass(remFlag, remPrivFlag, qty, tab1.walletPass.get(), coinType, remPW)
			elif(printPW == 2):
				Piper.genAndPrintKeys(remFlag, remPrivFlag, qty, tab1.walletPass.get(), coinType, remPW, keyGenType)
			else:
				#invalid option, return
				return
			
		
		except ValueError:
			print "Please enter an int!"
			qrPopup = QRPopup()
			qrPopup.showAlert("Error, enter an integer for the copies of wallet field!")
			#uncomment the 'raise' to make it print the real exception
			#raise
	
	def setEncryptYes(self):
		global tab1
		tab1.printPW.set(1)
		tab1.walletPass.set("")
		tab1.verPass.set("")
		tab1.passGroup.pack(padx=10, pady=10)
		tab1.remPWFrame.pack()
		tab1.printButton.forget()
		tab1.printButton.pack()
	
	
	def setAutomaticEncryptYes(self):
		global tab1
		tab1.printPW.set(1)
		tab1.walletPass.set("")
		tab1.verPass.set("")
		tab1.remPWFrame.pack()
		tab1.passGroup.forget()
		tab1.printButton.forget()
		tab1.printButton.pack()


	def setEncryptNo(self):
		global tab1
		tab1.printPW.set(2)
		tab1.walletPass.set("")
		tab1.verPass.set("")
		tab1.passGroup.forget()
		tab1.remPWFrame.forget()
	
	def setTradYes(self):
		global tab4
		tab4.tradFrame.pack()
		tab4.applyButton.forget()
		tab4.applyButton.pack()

	
	def setTradNo(self):
		self.setEncryptNo()
		global tab4
		tab4.coinType.set('Bitcoin')
		tab4.addrPrefix.set('1')
		tab4.headlessEnc.set('0')
		tab4.tradFrame.forget()

	def tabChangedEvent(self, event):
		if event.widget.index("current") == 2:
			global tab3
			tab3.populate()
		elif event.widget.index("current") == 4:
			global tab4
			tab4.populate()
		elif event.widget.index("current") == 0:
			global tab1
			tab1.checkTrad()
	
	def reprint(self, event):
		#print_keypair(pubkey, privkey, leftBorderText)
		Piper.print_keypair(event.widget.pubkey, event.widget.privkey, "Serial Number: "+str(event.widget.serialnum), event.widget.coinType)

	
	def showPassword(self, event):
		self.showMessage("Password of encrypted private key", event.widget.password)

	def showMessage(self, titleMsg, alertMsg):
		top = tk.Toplevel()
		top.geometry("700x90")
		top.title(titleMsg)

		tk.Label(top, text=alertMsg).pack(padx=10, pady=10)
		
		button = tk.Button(top, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10)





class DecryptedKeyPopup:
	
	def decryptKey(self):
		#try:
		self.decryptedKeyOnPopup.set(wallet_enc.decryptBIP0038(self.encryptedPrivKey, self.walletPass.get()))
		"""
		except:
			print "unexpected error: ",sys.exc_info()[0]
			top = tk.Toplevel()
			top.title("Error!")
			tk.Label(top, text="Incorrect password.").pack(padx=10, pady=10)
			button = tk.Button(top, text="Dismiss", command=top.destroy)
			button.pack(padx=10, pady=10)
		"""
	def showPopup(self, event):
		print event.widget.serialnum
		
		qrPopup = QRPopup()

		self.encryptedPrivKey = event.widget.privkey

		top = tk.Toplevel()
		top.title("Decrypted key")
		top.geometry("550x240")
		
		passGroup = tk.LabelFrame(top, text="Encrypted wallet password")
		passFrame = tk.Frame(passGroup)
		self.walletPass = tk.StringVar()
		tk.Label (passFrame, text='Enter password: ').pack(side=tk.LEFT,padx=10,pady=10)
		tk.Entry(passFrame, width=10, textvariable=self.walletPass, show="*").pack(side=tk.LEFT,padx=10,pady=10)
		passFrame.pack()
		
		passGroup.pack(padx=10, pady=10)

		decBut = tk.Button(top, text="Decrypt", command=self.decryptKey)
		decBut.pack(padx=10, pady=10)
		
		resultFrame = tk.Frame(top)
		tk.Label(resultFrame, text="Decrypted key").pack(side=tk.LEFT, padx=10, pady=10)
		self.decryptedKeyOnPopup = tk.StringVar()
		msg = tk.Entry(resultFrame, textvariable=self.decryptedKeyOnPopup, width=52)
		msg.pack(side=tk.LEFT)
		resultFrame.pack(padx=10, pady=10)

		
		buttonFrame = tk.Frame(top)
		qrBut = tk.Button(buttonFrame, text="Show QR Code")
		qrBut.bind("<Button-1>", qrPopup.showDecKeyPopup)
		qrBut.pack(padx=10, pady=10, side=tk.LEFT)
		qrBut.decKeyOnPopup = self.decryptedKeyOnPopup
		button = tk.Button(buttonFrame, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10, side=tk.LEFT)
		buttonFrame.pack()


class QRPopup:

	def showAlert(self, alertMsg):
		top = tk.Toplevel()
		top.geometry("400x90")
		top.title("Alert!")

		tk.Label(top, text=alertMsg).pack(padx=10, pady=10)
		
		button = tk.Button(top, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10)




		


	def showDecKeyPopup(self, event):
		self.show1CodePopup(event.widget.decKeyOnPopup.get())
		
	def showPopup(self, event):
		if event.widget.pubkey != "" and event.widget.privkey != "":
			self.show2CodePopup(event.widget)
		elif event.widget.pubkey != "":
			self.show1CodePopup(event.widget.pubkey)
		elif event.widget.privkey != "":
			self.show1CodePopup(event.widget.privkey)

	
	def show2CodePopup(self, widget):
		top = tk.Toplevel()
		top.title("QR Code")
	
		finalImg = Image.new("RGB", (1024, 650), "white")
		
		qr = qrcode.QRCode(
		    version=None,
		    error_correction=qrcode.constants.ERROR_CORRECT_M,
		    box_size=10,
		    border=0,
		)

		qr.add_data(widget.pubkey)
		qr.make(fit=True)

		qrImg = qr.make_image()
		
		font = ImageFont.truetype("/usr/share/fonts/ttf/ubuntu-font-family-0.80/UbuntuMono-R.ttf", 14)
		draw = ImageDraw.Draw(finalImg)
		draw.text((10, 500),"Public: "+widget.pubkey, font=font, fill=(0,0,0))

		finalImg.paste(qrImg, (30, 30))



		qr = qrcode.QRCode(
		    version=None,
		    error_correction=qrcode.constants.ERROR_CORRECT_M,
		    box_size=10,
		    border=0,
		)

		qr.add_data(widget.privkey)
		qr.make(fit=True)

		qrImg = qr.make_image()
			
		font = ImageFont.truetype("/usr/share/fonts/ttf/ubuntu-font-family-0.80/UbuntuMono-R.ttf", 14)
		draw = ImageDraw.Draw(finalImg)
		textToPrint = "Private: "+widget.privkey

		textSize = draw.textsize(textToPrint, font=font)
		
		charInd = 0
		lineInd = 0
		while(textSize[0] > 400):
			textInner = ""
			textSizeInner = draw.textsize(textInner, font=font)
			while(textSizeInner[0] < 390):
				textInner = textInner + textToPrint[charInd]
				textSizeInner = draw.textsize(textInner, font=font)
				charInd += 1

				
			draw.text((600, 360+(lineInd*15)),textInner, font=font, fill=(0,0,0))
			
			textSize = draw.textsize(textToPrint[charInd:], font=font)
			lineInd += 1
		
		draw.text((600, 360+(lineInd*15)),textToPrint[charInd:], font=font, fill=(0,0,0))
		finalImg.paste(qrImg.resize((300, 300)), (600, 30))



		finalImg.save("qrimg2.gif", "gif")
		
		
		
		
				
		qrPI = tk.PhotoImage(file="qrimg2.gif")
		label = tk.Label(top, image=qrPI)
		label.image = qrPI
		label.pack(padx=25, pady=25)	
		
		butFrame = tk.Frame(top)
		saveBut = tk.Button(butFrame, text="Save to Desktop")
		saveBut.bind("<Button-1>", self.saveDouble)
		saveBut.qrImg = finalImg
		saveBut.widgetData = widget
		saveBut.pack(padx=10, pady=10, side=tk.LEFT)

		button = tk.Button(butFrame, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10, side=tk.TOP)

		butFrame.pack(padx=10, pady=10)
	
	
	def show1CodePopup(self, dataToEncode):
		top = tk.Toplevel()
		top.title("QR Code")
		
		qr = qrcode.QRCode(
		    version=None,
		    error_correction=qrcode.constants.ERROR_CORRECT_M,
		    box_size=10,
		    border=0,
		)

		qr.add_data(dataToEncode)
		qr.make(fit=True)

		qrImg = qr.make_image()
		qrImg.save("qrimg1.gif", "gif")
				
		qrPI = tk.PhotoImage(file="qrimg1.gif")
		label = tk.Label(top, image=qrPI)
		label.image = qrPI
		label.pack(padx=25, pady=25)	
		
		butFrame = tk.Frame(top)
		saveBut = tk.Button(butFrame, text="Save to Desktop")
		saveBut.bind("<Button-1>", self.saveSingle)
		saveBut.qrImg = qrImg
		saveBut.qrData = dataToEncode
		saveBut.pack(padx=10, pady=10, side=tk.LEFT)

		button = tk.Button(butFrame, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10, side=tk.TOP)

		butFrame.pack(padx=10, pady=10)
	
	def saveSingle(self, event):
		paddedImg = Image.new("RGB", (390, 420), "white")
		paddedImg.paste(event.widget.qrImg, (30, 30))
		font = ImageFont.truetype("/usr/share/fonts/ttf/ubuntu-font-family-0.80/UbuntuMono-R.ttf", 14)
		draw = ImageDraw.Draw(paddedImg)
		draw.text((10, 400),event.widget.qrData, font=font, fill=(0,0,0))
		paddedImg.save("/home/pi/Desktop/QRCode1.png")		
		self.showAlert("Saved to the Desktop with filename QRCode1.png")	
	
	def saveDouble(self, event):
		event.widget.qrImg.save("/home/pi/Desktop/QRCode2.png")
		self.showAlert("Saved to the Desktop with filename QRCode2.png")	


class Tab1(tk.Frame):
	
	

	def __init__(self, root):
		tk.Frame.__init__(self, root)
		
		pUtil = PiperUtil()

		printGroup = tk.Frame(self)
		
		qtyFrame = tk.Frame(printGroup)
				
		
		self.walletQuantity = tk.StringVar()
		tk.Label (qtyFrame, text='Number of copies of wallet to print ').pack(side=tk.LEFT,padx=10,pady=10)
		qtyField = tk.Entry(qtyFrame, width=10, textvariable=self.walletQuantity)
		qtyField.pack(side=tk.LEFT, padx=10, pady=10)
		self.walletQuantity.set("1")
		
		qtyFrame.pack()
		
		
		rdoFrame = tk.Frame(printGroup)
		self.remKey = tk.IntVar()
		tk.Label (rdoFrame, text='Remember public key ').pack(side=tk.LEFT,padx=10,pady=10)
		remPubKeyBtn = tk.Radiobutton(rdoFrame, text="Yes", variable=self.remKey, value=1)
		remPubKeyBtn.pack(side=tk.LEFT)
		remPubKeyBtn.select()
		tk.Radiobutton(rdoFrame, text="No", variable=self.remKey, value=2).pack(side=tk.LEFT)
		rdoFrame.pack()
		

		rdoFrame2 = tk.Frame(printGroup)
		self.remPrivKey = tk.IntVar()
		tk.Label (rdoFrame2, text='Remember private key ').pack(side=tk.LEFT,padx=10,pady=10)
		remPrivKeyBtn = tk.Radiobutton(rdoFrame2, text="Yes", variable=self.remPrivKey, value=1)
		remPrivKeyBtn.pack(side=tk.LEFT)
		remPrivKeyBtn.select()
		tk.Radiobutton(rdoFrame2, text="No", variable=self.remPrivKey, value=2).pack(side=tk.LEFT)
		rdoFrame2.pack()
		
	
		
		self.rdoFrame3 = tk.Frame(printGroup)
		self.encKey = tk.IntVar()
		tk.Label (self.rdoFrame3, text='Encrypt private key ').pack(side=tk.LEFT,padx=10,pady=10)
		tk.Radiobutton(self.rdoFrame3, text="Manual Entry", variable=self.encKey, value=1, command=pUtil.setEncryptYes).pack(side=tk.LEFT)
		tk.Radiobutton(self.rdoFrame3, text="Automatic", variable=self.encKey, value=3, command=pUtil.setAutomaticEncryptYes).pack(side=tk.LEFT)
		encNoBtn = tk.Radiobutton(self.rdoFrame3, text="No", variable=self.encKey, value=2, command=pUtil.setEncryptNo)
		encNoBtn.pack(side=tk.LEFT)
		encNoBtn.select()
		self.rdoFrame3.pack()
		
		
		self.passGroup = tk.LabelFrame(printGroup, text="Encrypted wallet password")
		self.passAndVerFrame = tk.Frame(self.passGroup)
		passFrame = tk.Frame(self.passAndVerFrame)
		self.walletPass = tk.StringVar()
		tk.Label (passFrame, text='Enter password: ').pack(side=tk.LEFT,padx=10,pady=10)
		tk.Entry(passFrame, width=10, textvariable=self.walletPass, show="*").pack(side=tk.LEFT,padx=10,pady=10)
		passFrame.pack()
		
		verFrame = tk.Frame(self.passAndVerFrame)
		self.verPass = tk.StringVar()
		tk.Label (verFrame, text='Verify password: ').pack(side=tk.LEFT,padx=10,pady=10)
		tk.Entry(verFrame, width=10, textvariable=self.verPass, show="*").pack(side=tk.LEFT,padx=10,pady=10)
		
		verFrame.pack()
		self.passAndVerFrame.pack()


		rdoFrame4 = tk.Frame(self.passGroup)
		self.printPW = tk.IntVar()
		tk.Label (rdoFrame4, text='Print password').pack(side=tk.LEFT,padx=10,pady=10)
		printPasswdBtn = tk.Radiobutton(rdoFrame4, text="Yes", variable=self.printPW, value=1)
		printPasswdBtn.pack(side=tk.LEFT)
		printPasswdBtn.select()
		tk.Radiobutton(rdoFrame4, text="No", variable=self.printPW, value=2).pack(side=tk.LEFT)
		rdoFrame4.pack()



		self.remPWFrame = tk.Frame(printGroup)
		self.remPW = tk.IntVar()
		tk.Label (self.remPWFrame,text='Remember password ').pack(side=tk.LEFT,padx=10,pady=10)
		remPWBtn = tk.Radiobutton(self.remPWFrame, text="Yes", variable=self.remPW, value=1)
		remPWBtn.pack(side=tk.LEFT)
		remPWBtn.select()
		tk.Radiobutton(self.remPWFrame, text="No", variable=self.remPW, value=2).pack(side=tk.LEFT)



		self.printButton = tk.Button(printGroup, text='Print', command=pUtil.printWallet)
		
		self.printButton.pack(side=tk.TOP)
		
		
		printGroup.pack(padx=10, pady=10)

	def checkTrad(self):
			
		con = None
                try:
                        con = sqlite3.connect('/home/pi/Printer/settings.db3')
                        cur = con.cursor()
                        cur.execute("SELECT key, value FROM Settings;")
			# heatTime, coinType, addrPrefix, encType FROM piper_settings LIMIT 1;")
                        rows = cur.fetchall()
			settings = {}
			for row in rows:
				settings[row[0]] = row[1]

                except sqlite3.Error, e:
                        print("Error %s:" % e.args[0])
                        sys.exit(1)
                finally:
                        if con:
                                con.commit()
                                con.close()
                                    

		if settings['keyGenType'] == 'trad':
			self.rdoFrame3.pack()
			self.printButton.forget()
			self.printButton.pack()
		else:
			self.rdoFrame3.forget()
	


class Tab2(tk.Frame):
	def __init__(self, root):
		tk.Frame.__init__(self, root)
		#tk.Label(self, text="Test label2").pack()

		pUtil = PiperUtil()


		bulkGroup = tk.Frame(self)

		bulkQtyFrame = tk.Frame(bulkGroup)

		self.bulkQuantity = tk.StringVar()

		tk.Label (bulkQtyFrame, text='Number of wallets to print using settings from Print Wallet tab ').pack(side=tk.LEFT,padx=10,pady=10)
		tk.Entry(bulkQtyFrame, width=10, textvariable=self.bulkQuantity).pack(side=tk.LEFT,padx=10,pady=10)
		self.bulkQuantity.set(2)
		bulkQtyFrame.pack()

		printBulkButton = tk.Button(bulkGroup, text="Print Bulk", command=pUtil.printBulkWallet)
		printBulkButton.pack()


		bulkGroup.pack(padx=10, pady=10)


class Tab3(tk.Frame):
	def __init__(self, root):
		tk.Frame.__init__(self, root)
		self.viewKeysCanvas = tk.Canvas(self)
		self.viewKeysGroup = tk.Frame(self.viewKeysCanvas)
		self.viewKeysScrollbar = tk.Scrollbar(self, orient="vertical",
								command=self.viewKeysCanvas.yview)
		self.viewKeysCanvas.configure(yscrollcommand=self.viewKeysScrollbar.set)
		self.viewKeysScrollbar.pack(side="right", fill="y")
		self.viewKeysCanvas.pack(fill="both", expand=True)
		self.viewKeysCanvas.create_window(0, 0, window=self.viewKeysGroup, anchor="nw")
		self.viewKeysGroup.bind("<Configure>", self.on_frame_configure)
		self.viewKeysRefs = []
		self.populate()
	
	def populate(self):

		pUtil = PiperUtil()
		decKeyPopup = DecryptedKeyPopup()
		qrPopup = QRPopup()
		con = None
		try:
			con = sqlite3.connect('keys.db3')#'/home/pi/Printer/keys.db3')
			cur = con.cursor()    
			cur.execute("SELECT serialnum, public, private, coinType, password FROM keys")
			rows = cur.fetchall()
			
			for aKey in self.viewKeysRefs:
				aKey.destroy()

			self.viewKeysRefs = []
			
			
			for row in rows:
				aKeyGroup = tk.LabelFrame(self.viewKeysGroup, text="Serial num: "+str(row[0]))
				
				buttonFrame = tk.Frame(aKeyGroup)
				if row[1] != "" or row[2] != "":		
					reprintBut = tk.Button(buttonFrame, text="Reprint")
					reprintBut.bind("<Button-1>", pUtil.reprint)
					reprintBut.pack(padx=10, side=tk.LEFT)
					reprintBut.serialnum = row[0]
					reprintBut.pubkey = row[1]
					reprintBut.privkey = row[2]
					reprintBut.coinType = row[3]

					qrBut = tk.Button(buttonFrame, text="Show QR codes")
					qrBut.pack(padx=10, side=tk.LEFT)
					qrBut.bind("<Button-1>", qrPopup.showPopup)
					qrBut.pack(padx=10, side=tk.LEFT)
					qrBut.serialnum = row[0]
					qrBut.pubkey = row[1]
					qrBut.privkey = row[2]
					qrBut.coinType = row[3]

				coinTypeFrame = tk.Frame(aKeyGroup)
				tk.Label(coinTypeFrame, text="Coin type: "+row[3]).pack(padx=10, pady=10, side=tk.LEFT)
				coinTypeFrame.pack(padx=10, pady=10, side=tk.TOP)

				if(row[1] != ""):
					keyFrame = tk.Frame(aKeyGroup)
					tk.Label(keyFrame, text="Public key: ").pack(padx=10, pady=10, side=tk.LEFT)
					keystr = tk.StringVar()
					tk.Entry(keyFrame, textvariable=keystr, width=52).pack(padx=10, pady=10, side=tk.LEFT)
					keystr.set(row[1])
					keyFrame.pack(padx=10, pady=10, side=tk.TOP)
				if(row[2] != ""):
					keyFrame = tk.Frame(aKeyGroup)
					tk.Label(keyFrame, text="Private key: ").pack(padx=10, pady=10, side=tk.LEFT)
					keystr=tk.StringVar()
					tk.Entry(keyFrame, textvariable=keystr, width=52).pack(padx=10, pady=10, side=tk.LEFT)
					keystr.set(row[2])
					keyFrame.pack(padx=10, pady=10, side=tk.TOP)

				if(row[4] != ""):
					#the key is encrypted with a stored password
					aBut = tk.Button(buttonFrame, text="Reprint password")
					aBut.bind("<Button-1>", pUtil.reprintPassword)
					aBut.serialnum= str(row[0])
					aBut.pubkey = row[1]
					aBut.privkey = row[2]
					aBut.password = row[4]
					aBut.pack(padx=10, side=tk.LEFT)
					
					aBut2 = tk.Button(buttonFrame, text="View password")
					aBut2.bind("<Button-1>", pUtil.showPassword)
					aBut2.serialnum= str(row[0])
					aBut2.pubkey = row[1]
					aBut2.privkey = row[2]
					aBut2.password = row[4]
					aBut2.pack(padx=10, side=tk.LEFT)

				buttonFrame.pack(padx=10, pady=10)		
				aKeyGroup.pack(padx=10, pady=10)
				self.viewKeysRefs.append(aKeyGroup)
				
				
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
		finally:
			if con:
				con.commit()
				con.close()

	
	def on_frame_configure(self, event):
		"""Reset the scroll region to encompass the inner frame"""
		self.viewKeysCanvas.configure(scrollregion=self.viewKeysCanvas.bbox("all"))

class Tab4(tk.Frame):
	def __init__(self, root):
		tk.Frame.__init__(self, root)
		self.populate()
	def populate(self):
		for item in self.children.values():
			item.destroy()

		pUtil = PiperUtil()

		heatTimeFrame = tk.Frame(self)
		label0 = tk.Label (heatTimeFrame, text='Heat Time:')
		label0.pack(side=tk.LEFT,padx=10,pady=10)
		self.heatTime = tk.Scale(heatTimeFrame, from_=30, to=255, length=255, orient=tk.HORIZONTAL)
		self.heatTime.pack(side=tk.LEFT, padx=10, pady=0)
		heatTimeFrame.pack(padx=10, pady=10)
		

		label1 = tk.Label(self, text="Greater heat time means a darker print.  The default value for 20 year paper is 100.")
		label1.pack(padx=10, pady=5)


		pFwareFrame = tk.Frame(self)

		tk.Label(pFwareFrame, text="Printer firmware version:").pack(side=tk.LEFT, padx=10, pady=10)
		self.pFware = tk.StringVar()

		tk.Radiobutton(pFwareFrame, text="Less than 2.68", variable=self.pFware, value="old").pack(side=tk.LEFT, padx=10, pady=10)
		tk.Radiobutton(pFwareFrame, text="2.68 or greater", variable=self.pFware, value="new").pack(side=tk.LEFT, padx=10, pady=10)

		pFwareFrame.pack()




		keyGenTypeFrame = tk.Frame(self)

		label2 = tk.Label(keyGenTypeFrame, text="Key generation type:")
		label2.pack(side=tk.LEFT, padx=10, pady=10)
		self.keyGenType = tk.StringVar()

		tk.Radiobutton(keyGenTypeFrame, text="Traditional", variable=self.keyGenType, value="trad", command=pUtil.setTradYes).pack(side=tk.LEFT, padx=10, pady=10)
		tk.Radiobutton(keyGenTypeFrame, text="BIP0032", variable=self.keyGenType, value="bip0032", command=pUtil.setTradNo).pack(side=tk.LEFT, padx=10, pady=10)

		keyGenTypeFrame.pack()
		
		self.tradFrame = tk.Frame(self)	
		
		coinTypeFrame = tk.Frame(self.tradFrame)

		label3 = tk.Label(coinTypeFrame, text="Coin type:")
		label3.pack(side=tk.LEFT, padx=10, pady=10)
		self.coinType = tk.StringVar()



		
		con = None
                try:
                        con = sqlite3.connect('/home/pi/Printer/settings.db3')
                        cur = con.cursor()
                        cur.execute("SELECT key, value FROM Settings;")
			# heatTime, coinType, addrPrefix, encType FROM piper_settings LIMIT 1;")
                        rows = cur.fetchall()
			settings = {}
			for row in rows:
				settings[row[0]] = row[1]

			cur.execute("SELECT name FROM CoinFormats;")
			rows = cur.fetchall()
			options = []
			for row in rows:
				options.append(row[0])

                except sqlite3.Error, e:
                        print("Error %s:" % e.args[0])
                        sys.exit(1)
                finally:
                        if con:
                                con.commit()
                                con.close()
                                    




		self.opMenu = apply(tk.OptionMenu,(coinTypeFrame, self.coinType) + tuple(options))
		self.opMenu.pack(side=tk.LEFT, padx=10, pady=10)

		coinTypeFrame.pack()


		addressPrefixFrame = tk.Frame(self.tradFrame)
		label5 = tk.Label(addressPrefixFrame, text="Address prefix")
		label5.pack(side=tk.LEFT, padx=10, pady=10)

		self.addrPrefix = tk.StringVar()
		tk.Entry(addressPrefixFrame, textvariable=self.addrPrefix).pack(side=tk.LEFT, padx=10, pady=10)
		addressPrefixFrame.pack()
		
		tk.Label(self.tradFrame, text="Address prefix must begin with 1 for bitcoin and L for litecoin or key generation will fail.").pack(padx=10)
		tk.Label(self.tradFrame, text="We do not recommend a prefix longer than 3 characters.  ").pack(padx=10)
		tk.Label(self.tradFrame, text="A prefix just 3 characters long can take up to 30 seconds to generate (for example 1CC).").pack(padx=10)
		
		headlessEncryptFrame = tk.Frame(self.tradFrame)

		tk.Label(headlessEncryptFrame, text="Automatically encrypt private key:").pack(side=tk.LEFT, padx=10, pady=10)
		self.headlessEnc = tk.StringVar()

		tk.Radiobutton(headlessEncryptFrame, text="On", variable=self.headlessEnc, value="1").pack(side=tk.LEFT, padx=10, pady=10)
		tk.Radiobutton(headlessEncryptFrame, text="Off", variable=self.headlessEnc, value="0").pack(side=tk.LEFT, padx=10, pady=10)

		headlessEncryptFrame.pack()


		randPwLengthFrame = tk.Frame(self.tradFrame)
		tk.Label (randPwLengthFrame, text='Automatic password word length:').pack(side=tk.LEFT,padx=10,pady=0)
		self.randPwLength = tk.Scale(randPwLengthFrame, from_=1, to=16, length=255, orient=tk.HORIZONTAL)
		self.randPwLength.pack(side=tk.LEFT, padx=10, pady=0)
		randPwLengthFrame.pack(padx=10, pady=0)
		

		self.applyButton = tk.Frame(self)

		setButton = tk.Button(self.applyButton, text="Apply settings", command=self.applySettings)
		setButton.pack(padx=10, pady=10)
		label6 = tk.Label(self.applyButton, text="These settings will be stored and used when printing in headless mode as well.")
		label6.pack(padx=10)

	        self.heatTime.set(settings['heatTime'])
		self.coinType.set(settings['cointype'])
		self.addrPrefix.set(settings['addrPrefix'])
		self.headlessEnc.set(settings['headlessEnc'])
		self.randPwLength.set(settings['randomPasswordLength'])
		self.keyGenType.set(settings['keyGenType'])
		self.pFware.set(settings['printerFirmware'])


		if settings['keyGenType'] == "trad":
			self.tradFrame.pack()
		else:
			global tab1
			tab1.rdoFrame3.forget()
			tab1.printPW.set(2)
			tab1.walletPass.set("")
			tab1.verPass.set("")


		self.applyButton.pack()



		"""
		m = self.opMenu.children['menu']
		m.delete(0, tk.END)

	
		con = None
                try:
                        con = sqlite3.connect('/home/pi/Printer/settings.db3')
                        cur = con.cursor()
                        cur.execute("SELECT key, value FROM Settings;")
			# heatTime, coinType, addrPrefix, encType FROM piper_settings LIMIT 1;")
                        rows = cur.fetchall()
			settings = {}
			for row in rows:
				settings[row[0]] = row[1]

			cur.execute("SELECT name FROM CoinFormats;")
			rows = cur.fetchall()
			options = []
			for row in rows:
				options.append(row[0])

                except sqlite3.Error, e:
                        print("Error %s:" % e.args[0])
                        sys.exit(1)
                finally:
                        if con:
                                con.commit()
                                con.close()
                                    



		for val in options:
			m.add_command(label=val, command=lambda v=self.coinType, l=val:v.set(1))
		self.coinType.set(settings['cointype'])
		"""	
			
	def applySettings(self):
		

		try:
			con = sqlite3.connect('/home/pi/Printer/settings.db3')
			cur = con.cursor()
			cur.execute("SELECT versionNum, prefix FROM CoinFormats WHERE name=?",(self.coinType.get(),))
			row = cur.fetchone()
			versionNum = row[0]
			defaultPrefix = row[1]
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
		
		#second, check that prefix is valid
		
		if(len(self.addrPrefix.get()) == 0 or self.addrPrefix.get()[0] != defaultPrefix):
			self.showMessage("Error!!","Invalid prefix.  "+self.coinType.get()+" addresses must begin with "+defaultPrefix) 
			return

		process = Popen(["./vanitygen", "-q","-n", "-t","1","-s", "/dev/random", "-X", str(versionNum), self.addrPrefix.get()], stderr=PIPE)

		
		results = process.stderr.read().lower()
		#print results
		if "prefix" in results:		
			prefixValid = False
		else:
			prefixValid = True

		if (prefixValid == False):
			self.showMessage("Error!!","Invalid address prefix.  Not all characters are valid.") 
			return
		
		
		try:
		        con.execute("UPDATE Settings SET value=? WHERE key='heatTime';", (str(self.heatTime.get()),))
			con.execute("UPDATE Settings SET value=? WHERE key='cointype';", (self.coinType.get(),))
			con.execute("UPDATE Settings SET value=? WHERE key='addrPrefix';", (self.addrPrefix.get(),))
			#con.execute("UPDATE Settings SET value=? WHERE key='encType';", (self.encType.get(),))
			con.execute("UPDATE Settings SET value=? WHERE key='headlessEnc';", (self.headlessEnc.get(),))
			con.execute("UPDATE Settings SET value=? WHERE key='randomPasswordLength';", (self.randPwLength.get(),))
			con.execute("UPDATE Settings SET value=? WHERE key='keyGenType';", (self.keyGenType.get(),))
			con.execute("UPDATE Settings SET value=? WHERE key='printerFirmware';", (self.pFware.get(),))
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
		finally:
			if con:
				con.commit()
				con.close()
		self.showMessage("Success!","Settings saved.") 


	def showMessage(self, titleMsg, alertMsg):
		top = tk.Toplevel()
		top.geometry("500x90")
		top.title(titleMsg)

		tk.Label(top, text=alertMsg).pack(padx=10, pady=10)
		
		button = tk.Button(top, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10)





class Tab5(tk.Frame):
	def __init__(self, root):
		tk.Frame.__init__(self, root)
	
		SSSSFrame = tk.LabelFrame(self, text="Shamir's Secret Sharing Scheme")

		textBoxFrameSSSS = tk.Frame(SSSSFrame)
		tk.Label(textBoxFrameSSSS, text="Secret to be split").pack(side=tk.LEFT, padx=10, pady=10)
		self.SSSStextBox = tk.StringVar()
		tk.Entry(textBoxFrameSSSS, textvariable=self.SSSStextBox).pack(side=tk.LEFT, padx=10, pady=10)
		textBoxFrameSSSS.pack()

		ddFrame = tk.Frame(SSSSFrame)
		tk.Label(ddFrame, text="Require").pack(side=tk.LEFT, padx=10)
		self.k = tk.StringVar()
		self.n = tk.StringVar()
		options = []
		for r in range(1,20):
			options.append(str(r))

		opMenu = apply(tk.OptionMenu,(ddFrame, self.k) + tuple(options))
		opMenu.pack(side=tk.LEFT, padx=10, pady=10)
		self.k.set("3")
		tk.Label(ddFrame, text=" of ").pack(side=tk.LEFT)
		
		opMenuN = apply(tk.OptionMenu,(ddFrame, self.n) + tuple(options))
		opMenuN.pack(side=tk.LEFT, padx=10, pady=10)
		self.n.set("5")
		tk.Label(ddFrame, text="parts to reconstruct the secret").pack(side=tk.LEFT, padx=10)

		ddFrame.pack()


		buttonHolderSSSS = tk.Frame(SSSSFrame)

		printButtonSSSS = tk.Button(buttonHolderSSSS, text="Print shares", command=self.splitAndPrint)
		printButtonSSSS.pack(side=tk.LEFT, padx=10, pady=10)
		

		buttonHolderSSSS.pack()
		SSSSFrame.pack(padx=10, pady=10)	
		
		printMiscFrame = tk.LabelFrame(self, text="Print Miscellaneous Text")

		textBoxFrame = tk.Frame(printMiscFrame)
		tk.Label(textBoxFrame, text="To be printed").pack(side=tk.LEFT, padx=10, pady=10)
		self.textBox = tk.StringVar()
		tk.Entry(textBoxFrame, textvariable=self.textBox).pack(side=tk.LEFT, padx=10, pady=10)
		textBoxFrame.pack()

		
		buttonHolder = tk.Frame(printMiscFrame)

		printAsTextButton = tk.Button(buttonHolder, text="Print as text", command=self.printAsText)
		printAsTextButton.pack(side=tk.LEFT, padx=10, pady=10)
		
		printAsQRButton = tk.Button(buttonHolder, text="Print as QR code", command=self.printAsQR)
		printAsQRButton.pack(side=tk.LEFT, padx=10, pady=10)
		

		buttonHolder.pack()
		printMiscFrame.pack(padx=10, pady=10)
		
		AddAltFrame = tk.Frame(self)


		AddAltButton = tk.Button(AddAltFrame, text="Add Alt Coin", command=self.launchAddAlt)
		AddAltButton.pack(padx=10, pady=10)
		
		AddAltFrame.pack(padx=10, pady=10)

	"""
		HDMFrame = tk.LabelFrame(self, text="Print HDM Wallet Seed")


		HDMButton = tk.Button(HDMFrame, text="Print seed", command=self.printHDMSeed)
		HDMButton.pack(padx=10, pady=10)
		
		HDMFrame.pack(padx=10, pady=10)
		

	def printHDMSeed(self):
		HDMWallet.printHDMWalletSeed()
	"""		
	def launchAddAlt(self):
		acm = AltCoinMan()
		acm.title("Add Coin")



	def splitAndPrint(self):
		pUtil = PiperUtil()
		pUtil.splitAndPrint(self.SSSStextBox.get(), self.k.get(), self.n.get())
	
	

	def printAsText(self):
		pUtil = PiperUtil()
		pUtil.printAsText(self.textBox.get())
	
	def printAsQR(self):
		pUtil = PiperUtil()
		pUtil.printAsQR(self.textBox.get())



	def showMessage(self, titleMsg, alertMsg):
		top = tk.Toplevel()
		top.geometry("400x90")
		top.title(titleMsg)

		tk.Label(top, text=alertMsg).pack(padx=10, pady=10)
		
		button = tk.Button(top, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10)




class AltCoinMan(tk.Toplevel):
	def __init__(self):
		tk.Toplevel.__init__(self)

		pUtil = PiperUtil()
		"""
		

		coinTypeFrame = tk.Frame(self)

		tk.Label(coinTypeFrame, text="Coin type:").pack(side=tk.LEFT, padx=10, pady=10)
		self.coinType = tk.StringVar()
		self.coinType.trace('w', self.coinTypeChanged)


		
		con = None
                try:
                        con = sqlite3.connect('/home/pi/Printer/settings.db3')
                        cur = con.cursor()
                        cur.execute("SELECT key, value FROM Settings;")
			# heatTime, coinType, addrPrefix, encType FROM piper_settings LIMIT 1;")
                        rows = cur.fetchall()
			settings = {}
			for row in rows:
				settings[row[0]] = row[1]

			cur.execute("SELECT name FROM CoinFormats;")
			rows = cur.fetchall()
			options = ["New Coin Type"]
			for row in rows:
				options.append(row[0])



                except sqlite3.Error, e:
                        print("Error %s:" % e.args[0])
                        sys.exit(1)
                finally:
                        if con:
                                con.commit()
                                con.close()
                                    




		opMenu = apply(tk.OptionMenu,(coinTypeFrame, self.coinType) + tuple(options))
		opMenu.pack(side=tk.LEFT, padx=10, pady=10)

		coinTypeFrame.pack()
		"""
		
		self.coinNameHolder = tk.Frame(self)
		self.coinNameFrame = tk.Frame(self.coinNameHolder)
		tk.Label(self.coinNameFrame, text="New Coin Name").pack(side=tk.LEFT, padx=10, pady=10)
		self.newCoinName = tk.StringVar()
		tk.Entry(self.coinNameFrame, textvariable=self.newCoinName).pack(side=tk.LEFT, padx=10, pady=10)
		self.coinNameFrame.pack()
		tk.Label(self.coinNameHolder, text="This is the name of the alt-coin that you're adding.  Bitcoin, Litecoin, Dogecoin etc.").pack(padx=10)
		self.coinNameHolder.pack()


		addressPrefixFrame = tk.Frame(self)
		tk.Label(addressPrefixFrame, text="Address Prefix").pack(side=tk.LEFT, padx=10, pady=10)
		self.addrPrefix = tk.StringVar()
		tk.Entry(addressPrefixFrame, textvariable=self.addrPrefix).pack(side=tk.LEFT, padx=10, pady=10)
		addressPrefixFrame.pack()
		tk.Label(self, text="This is the address prefix for the coin's public addresses.").pack(padx=10)
		tk.Label(self, text="On Bitcoin, this is a 1.  Dogecoin is D, and Litecoin is L.").pack(padx=10)

		versionNumFrame = tk.Frame(self)
		tk.Label(versionNumFrame, text="Version Code").pack(side=tk.LEFT, padx=10, pady=10)
		self.versionNum = tk.StringVar()
		tk.Entry(versionNumFrame, textvariable=self.versionNum).pack(side=tk.LEFT, padx=10, pady=10)
		versionNumFrame.pack()
		tk.Label(self, text="This is the address version number that is provided as the -X parameter to vanitygen.").pack(padx=10)

		bgImgFrame = tk.Frame(self)
		tk.Label(bgImgFrame, text="Wallet Background Image").pack(side=tk.LEFT, padx=10, pady=10)
		self.bgImg = tk.StringVar()
		tk.Entry(bgImgFrame, textvariable=self.bgImg).pack(side=tk.LEFT, padx=10, pady=10)
		bgImgFrame.pack()
		tk.Label(self, text="This is the prefix for the image filename of the wallet background image.").pack(padx=10)
		tk.Label(self, text="If you're not sure what to put here, put the word blank.").pack(padx=10)
		tk.Label(self, text="The image files live in /home/pi/Printer/Images.").pack(padx=10)
		
		self.applyButton = tk.Frame(self)

		setButton = tk.Button(self.applyButton, text="Add Coin", command=self.applySettings)
		setButton.pack(padx=10, pady=10)
		

		self.applyButton.pack()


	def applySettings(self):
		
		try:

			con = sqlite3.connect('/home/pi/Printer/settings.db3')
		        con.execute("INSERT OR REPLACE INTO CoinFormats (versionNum, prefix, bgfile, name) VALUES (?,?,?,?);", (self.versionNum.get(), self.addrPrefix.get(), self.bgImg.get(), self.newCoinName.get()))
		except sqlite3.Error, e:
			print "Error %s:" % e.args[0]
			sys.exit(1)
		finally:
			if con:
				con.commit()
				con.close()
		self.destroy()
		self.showMessage("Success!","Coin added!") 
		"""
	def coinTypeChanged(self, name, index, mode):
		print 'new coin type: '+self.coinType.get()
		#prefill the fields
		if self.coinType.get() != 'New Coin Type':	
			try:
				con = sqlite3.connect('/home/pi/Printer/settings.db3')
				cur = con.cursor()
				cur.execute("SELECT versionNum, prefix, bgfile FROM CoinFormats WHERE name=?",(self.coinType.get(),))
				row = cur.fetchone()
				versionNum = row[0]
				defaultPrefix = row[1]
				bgImg = row[2]
			except sqlite3.Error, e:
				print "Error %s:" % e.args[0]
				sys.exit(1)
		

			self.hideNameField()
			self.addrPrefix.set(defaultPrefix)
			self.versionNum.set(versionNum)
			self.bgImg.set(bgImg)
		else:	
			self.showNameField()
			self.addrPrefix.set('')
			self.versionNum.set('')
			self.bgImg.set('blank')

	def hideNameField(self):
		self.coinNameHolder.pack_forget()

	def showNameField(self):
		self.applyButton.pack_forget()
		self.coinNameHolder.pack()
		self.applyButton.pack()
		"""
	def showMessage(self, titleMsg, alertMsg):
		top = tk.Toplevel()
		top.geometry("500x90")
		top.title(titleMsg)

		tk.Label(top, text=alertMsg).pack(padx=10, pady=10)
		
		button = tk.Button(top, text="Dismiss", command=top.destroy)
		button.pack(padx=10, pady=10)








def rClicker(e):
    ''' right click context menu for all Tk Entry and Text widgets
    '''

    try:
        def rClick_Copy(e, apnd=0):
            e.widget.event_generate('<Control-c>')

        def rClick_Cut(e):
            e.widget.event_generate('<Control-x>')

        def rClick_Paste(e):
            e.widget.event_generate('<Control-v>')

        e.widget.focus()

        nclst=[
               (' Cut', lambda e=e: rClick_Cut(e)),
               (' Copy', lambda e=e: rClick_Copy(e)),
               (' Paste', lambda e=e: rClick_Paste(e)),
               ]

        rmenu = tk.Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except tk.TclError:
        print ' - rClick menu, something wrong'
        pass

    return "break"


def rClickbinder(r):

    try:
        for b in [ 'Text', 'Entry', 'Listbox', 'Label']: #
            r.bind_class(b, sequence='<Button-3>',
                         func=rClicker, add='')
    except tk.TclError:
        print ' - rClickbinder, something wrong'
        pass







pUtil = PiperUtil()

root = tk.Tk()
sizex, sizey, posx, posy = 700, 495, 200, 10
root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))
root.title('Piper Wallet')

note = ttk.Notebook(root)
tab1 = Tab1(note)
tab2 = Tab2(note)
tab3 = Tab3(note)
tab4 = Tab4(note)
tab5 = Tab5(note)
#tab6 = Tab6(note)

note.add(tab1, text="Print Wallet")
note.add(tab2, text="Bulk Wallets")
note.add(tab3, text="View Keys")
note.add(tab5, text="Utilities")
note.add(tab4, text="Settings")
#note.add(tab6, text="Alt-coins")
#note.add(tab4, text = "Encryption Utility")
note.bind_all("<<NotebookTabChanged>>", pUtil.tabChangedEvent)


note.pack(expand=True, fill="both")


rClickbinder(root)

root.mainloop()
