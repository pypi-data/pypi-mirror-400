import pyotp
key = 'X77U2PFM6EQKNF63TJOUIBKHTEF267LK'
totp = pyotp.TOTP(key)
print(totp.now())