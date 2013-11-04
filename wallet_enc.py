#this code was mostly taken and modified from the electrum project located here: https://github.com/spesmilo/electrum


import base64
import hashlib
import aes
import sqlite3
import serializeBTC as ser
import Crypto.Cipher.AES as AES
import Crypto.Hash.SHA256 as SHA256
import scrypt
from itertools import izip
from array import array
from bitcoin.bip38 import Bip38
from bitcoin.key import CKey
from bitcoin.base58 import CBase58Data, CBitcoinAddress

Hash = lambda x: hashlib.sha256(hashlib.sha256(x).digest()).digest()

# AES encryption
EncodeAES = lambda secret, s: b58encode(aes.encryptData(secret,s))
DecodeAES = lambda secret, e: aes.decryptData(secret, b58decode(e))

# Electrum uses base64, which is fine when it's stored in the computer, but base58 was created for readibiity by humans
# AES encryption
#EncodeAES = lambda secret, s: base64.b64encode(aes.encryptData(secret,s))
#DecodeAES = lambda secret, e: aes.decryptData(secret, base64.b64decode(e))


#BIO0038
def encryptBIP0038(pubkey, privkey, secret):
	k = CKey()
	#decode the wallet import format by base58 decoding then dropping the last 4 bytes and the first byte
	decoded = b58decode(privkey)
	decoded = decoded[:-4]
	decoded = decoded[1:]
	k.generate(decoded)
	k.set_compressed(False)
	b = Bip38(k, secret)
	return str(CBase58Data(b.get_encrypted(), 0x01))       
	

def pw_encode(pub, priv, password):
    if password:

        secret = Hash(password)
	con = None
	encType = ""	
	try:
		con = sqlite3.connect('/home/pi/Printer/keys.db3')
		cur = con.cursor()
		cur.execute("SELECT encType FROM piper_settings LIMIT 1;")
		row = cur.fetchone()
		encType = row[0]
	except sqlite3.Error, e:
		print("Error %s:" % e.args[0])
		sys.exit(1)
	finally:
		if con:
			con.commit()
			con.close()

	if encType == "aes":
        	return EncodeAES(secret, priv)
	elif encType == "bip0038":
		#do not pass in secret, pass in password, because the BIP0038 spec doesn't specify that you should hash passwords first in this way like with AES
		return encryptBIP0038(pub, priv, password) 
    else:
        return priv

def pw_decode(s, password):
    if password is not None:
        secret = Hash(password)
        try:
        	d = DecodeAES(secret, s)
        except:
            raise BaseException('Invalid password')
        return d
    else:
        return s



__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)

def b58encode(v):
    """ encode v, which is a string of bytes, to base58."""
    print "v length: "+str(len(v))+"\n"

    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += (256**i) * ord(c)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    nPad = 0
    for c in v:
        if c == '\0': nPad += 1
        else: break

    return (__b58chars[0]*nPad) + result

def b58decode(v):
    """ decode v into a string of bytes."""
    long_value = 0L
    for (i, c) in enumerate(v[::-1]):
        long_value += __b58chars.find(c) * (__b58base**i)

    result = ''
    while long_value >= 256:
        div, mod = divmod(long_value, 256)
        result = chr(mod) + result
        long_value = div
    result = chr(long_value) + result

    nPad = 0
    for c in v:
        if c == __b58chars[0]: nPad += 1
        else: break

    result = chr(0)*nPad + result
    
    return result


def EncodeBase58Check(vchIn):
    hash = Hash(vchIn)
    return b58encode(vchIn + hash[0:4])

def DecodeBase58Check(psz):
    vchRet = b58decode(psz, None)
    key = vchRet[0:-4]
    csum = vchRet[-4:]
    hash = Hash(key)
    cs32 = hash[0:4]
    if cs32 != csum:
        return None
    else:
        return key
