"""
    log.py
    Logging code for ScalyMUCK
    Copyright (c) 2012 Liukcairo
"""

_target_file = None
_echo = False
def set_target(target_file):
	file_handle = None
	try:
		file_handle = open(target_file, 'w')
		file_handle.write('ScalyMUCK Copyright (c) 2012 Liukcairo\n\n')
	except:
		return False
	file_handle.close()
	_target_file = target_file
	return True

def write(data):
	if (_target_file is None):
		return False
	file_handle = open(_target_file, 'a')
	file_handle.write(data + '\n')
	file_handle.close()
	
	if (_echo is True):
		print(data)
		
	return True

def get_target():
	return _target_file
	
def is_ready():
	if (_target_file is None):
		return False
	else:
		return True

def set_echo(status):
	_echo = status