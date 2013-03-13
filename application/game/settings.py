"""
	settings.py

	Basic settings loader.
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

class Settings:
	_settings_entries = { }
	_yes = ['1', 'true', 'y', 'yes', 'enable', 'toggle', 'enabled']		
    
	def __init__(self, target_file):
		try:
			file_handle = open(target_file, 'r')
        	except IOError:
            		return

        	for line_data in file_handle:
			preference_data = string.split(line_data, '=')
			line_data = line_data.lstrip()

			if (len(preference_data) == 2):
				data = preference_data[1]
				self._settings_entries[preference_data[0]] = data[:len(data)-1]
			elif(line_data.find('#') and line_data != ''):
				continue

		file_handle.close()

	def get_index(self, index, data_type):
		if(index in self._settings_entries):
			entries = self._settings_entries
			if (data_type is bool):
				if (string.lower(self._settings_entries[index]) in self._yes):
					return True
				else:
					return False
			else:
				return data_type(entries[index])
		else:
			return None
