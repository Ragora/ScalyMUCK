"""
	__init__.py
    
	ScalyMUCK's Mod manager code, it's used
	to import functionality from all sorts
	of installed modifications.
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import os
import string
import types

class Mod():
	name = None
	description = None
	author = None
	commands = None
	callbacks = None
	
	version_major = None
	version_minor = None
	version_revision = None
	
	server_version_major = None
	server_version_minor = None
	server_version_revision = None

def get_mod_list():
	files = os.listdir('modman/')
	
	mod_list = [ ]
	for file in files:
		if (string.find(file, '.') == -1):
			try:
				with open('modman/' + file + '/__init__.py') as f:
					pass
			except IOError:
					continue
			mod_list.append(file)
	return mod_list

def load_mod(name, logger):
	if (name in get_mod_list()):
		try:
			imported =  __import__('modman.' + name, globals(), locals(), [''], -1)
		except:
			logger.write('Warning: Failed to load modification: ' + name)
			return None
		
		mod_data = Mod()
		try:
			mod_data.name = imported.name
			mod_data.description = imported.description
			mod_data.author = imported.author
			mod_data.version_major = imported.version_major
			mod_data.version_minor = imported.version_minor
			mod_data.version_revision = imported.version_revision
			mod_data.server_version_major = imported.server_version_major
			mod_data.server_version_minor = imported.server_version_minor
			mod_data.server_version_revision = imported.server_version_revision
		except:
			logger.write('Warning: Failed to load modification: ' + name)
			return

		try:
			mod_data.commands = imported.get_commands()
		except:
			logger.write('Warning: Failed to load command listing from modification: ' + name)
			mod_data.commands = None

		try:
			mod_data.callbacks = imported.get_callbacks()
		except:
			logger.write('Warning: Failed to load callback listing from modification: ' + name)
			mod_data.callbacks = None
		
		return mod_data
	else:
		return None

def load_mods(logger):
	list = get_mod_list()
	mods = { }
	for mod in list:
		mod_data = load_mod(mod, logger)
		if (mod_data is None):
			continue

		mods[mod] = { 'Commands': { }, 'Callbacks': { } }

		mod_version = '%s.%s.%s' % (str(mod_data.version_major), str(mod_data.version_minor), str(mod_data.version_revision))
		logger.write('Name: ' + mod_data.name)
		logger.write('Author: ' + mod_data.author)
		logger.write('Version: ' + mod_version)
		logger.write('Description: ' + mod_data.description)

		logger.write('Attempting to load modification ...')

		# Loading all of our user chat commands
		mod_commands = mod_data.commands
		if (mod_commands is not None):
			logger.write('Total Commands: ' + str(len(mod_commands)))
			for mod_command in mod_commands:
				if (mod_commands[mod_command].has_key('Command') is False or type(mod_commands[mod_command]['Command']) is not types.FunctionType):
					logger.write('Warning: Failed to load command "' + mod_command + '" from modification "' + mod_data.name + '"!')
				else:
					if (mod_commands[mod_command].has_key('Description') is False):
						logger.write('Warning: Failed to load command description for "' + mod_command + '" from modification "' + mod_data.name + '"!')
						mod_commands[mod_command]['Description'] = '<An error has occurred in the modloader>'
					else:
						mod_commands[mod_command]['Description'] = str(mod_commands[mod_command]['Description'])
						mods[mod]['Commands'][mod_command] = mod_commands[mod_command]
		else:
			logger.write('Total Commands: 0')

		# Loading all of the callbacks
		"""
		callbacks = mod_data.callbacks
		if (callbacks is not None):
			logger.write('Total Callbacks: ' + str(len(callbacks)))	
			for callback in callbacks:
				if (type(callbacks[callback]) is not function):
					logger.write('Warning: Failed to load callback "' + callback + '" from modification "' + mod_data.name + '"!')
				else:
					self.callback_entries[callback].append(callbacks[callback])
		else:
			logger.write('Total Callbacks: 0')
		"""	

		logger.write(' ')

	return mods
