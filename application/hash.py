"""
	hash.py
	Hash Functions for ScalyMUCK
	Copyright (c) 2012 Liukcairo
"""

# No standard library imports

import bcrypt

# No project-specific library imports

def generate_hash(password):
	# 10 is the work factor
	hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(10))
	return hashed_password

def check_password(password, hash):
	if (bcrypt.hashpw(password, hash) == hash):
		return True
	else:
		return False
	
"""
# This was the old Hash code
import hashlib
from os import urandom
from base64 import b64encode, b64decode
from itertools import izip

from pbkdf2 import pbkdf2_bin

### Parameters -- temporarily stored here
SALT_LENGTH = 12
KEY_LENGTH = 24
HASH_FUNCTION = 'sha256'
COST_FACTOR = 10000

### Developed from http://exyr.org/2011/hashing-passwords/
def generate_hash(password):
	if isinstance(password, unicode):
		password = password.encode('utf-8')
	salt = b64encode(urandom(SALT_LENGTH))
	return 'PBKDF2${}${}${}${}'.format(HASH_FUNCTION, COST_FACTOR, salt,
		b64encode(pbkdf2_bin(password, salt, COST_FACTOR, KEY_LENGTH,
		getattr(hashlib, HASH_FUNCTION))))
		
def check_password(password, hash_):
	if isinstance(password, unicode):
		password = password.encode('utf-8')
	algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')
	assert algorithm == 'PBKDF2'
	hash_a = b64decode(hash_a)
	hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
		getattr(hashlib, hash_function))
	assert len(hash_a) == len(hash_b)
	diff = 0
	for char_a, char_b in izip(hash_a, hash_b):
		diff |= ord(char_a) ^ ord(char_b)
	return diff == 0
"""
