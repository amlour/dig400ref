"""
simple md5 with salt

import hashlib

user_password = "cookies"
salt = "thinmints"
new_password = user_password + salt 
hashpass = hashlib.md5(new_password.encode())
print(hashpass.hexdigest())

"""

from passlib.hash import sha256_crypt

salt = "password3"

pass1 = "password1" + salt
pass2 = "password2" + salt

saltpass1 = sha256_crypt.encrypt(pass1)
saltpass2 = sha256_crypt.encrypt(pass2)

print(saltpass1)
print(saltpass2)

print(sha256_crypt.verify("password1"+salt, saltpass1))




