"""
	settings.py
	This is the code that performs the configuration
	loading of ScalyMUCK.
	Copyright (c) 2012 Liukcairo
"""

import string
import log

class Settings:
	_settings_entries = { }
    
	def __init__(self, target_file):
		try:
			file_handle = open(target_file, 'r')
        	except IOError:
            		return

        	for line_data in file_handle:
			preference_data = string.split(line_data, '=')
			line_data = line_data.lstrip()

			# We need to make sure we actully got a list with at 2 values, any less and the program would crash.
			if (len(preference_data) == 2):
				self._settings_entries[preference_data[0]] = preference_data[1]
			elif(line_data.find('#') and line_data != ''):
				log.write('Warning: Located malformed configuration data in ' + target_file + ': ' + line_data)
				continue

		file_handle.close()

	def get_index(self, index):
		if(index in self._settings_entries):
			return self._settings_entries[index]
		else:
			return None
