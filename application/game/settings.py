"""
	Basic settings loader that provides easy to use functionality to load from simple
	configuration files that have take the following form on every line:
	
	* Option=Yes
	* Number=20
	* String=Whatever

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

class Settings:
	""" The Settings loader class provides simple functionality to load from simple configuration files. """
	_settings_entries = None
	_yes = ['1', 'true', 'y', 'yes', 'enable', 'toggle', 'enabled']		
    
	def __init__(self, target_file):
		""" Initializes an instance of the Settings loader. """
		self._settings_entries = { }
		self.load(target_file)

	def load(self, target_file):
		""" Loads a configuration file from the hard disk. """
		try:
			file_handle = open(target_file, 'r')
        	except IOError:
            		return

        	for line_data in file_handle:
			preference_data = string.split(line_data, '=')
			line_data = line_data.lstrip()

			if (len(preference_data) == 2):
				data = preference_data[1]
				entry_data = data[:len(data)].replace('\n','')
				entry_data = entry_data.replace("\r", "")
				self._settings_entries[preference_data[0]] = entry_data
			# TODO: Make this actually do some work to make post-fix comments work ...
			elif(line_data.find('#') and line_data != ''):
				continue

		file_handle.close()

	def get_indices(self):
		""" Returns all known indices. This is a list of the indices you would use in :func:`get_index`. """
		return self._settings_entries.keys()

	def get_index(self, index=None, datatype=None):
		""" Returns a loaded configuration setting from the Settings loader.

		Keyword arguments:
			* index -- The name of the setting that is to be loaded from the file.
			* datatype -- The datatype that is supposed to be used to represent this setting in the return value.

		"""
		if(index in self._settings_entries):
			entries = self._settings_entries
			if (datatype is bool):
				if (string.lower(self._settings_entries[index]) in self._yes):
					return True
				else:
					return False
			else:
				return datatype(entries[index])
		else:
			return None
