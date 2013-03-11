"""
	interface.py

	Basically the user interface for ScalyMUCK.
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

import modman

class Interface:
	_command_entries = { }
	_logger = None
	_debug_mode = False
	_world_instance = None
	_callback_entries = {
		'onClientAuthenticated': [ ],
		'onClientConnected': [ ],
		'onMessageSent': [ ]
	}

	def __init__(self, logger, debug_mode):
		mods = modman.load_mods(logger)
		for mod in mods:
			if ('Commands' in mods[mod]):
				commands = mods[mod]['Commands']
				for command in commands:
					self._command_entries[command] = commands[command]
		self.debug_mode = debug_mode
		if (debug_mode):
			logger.write('Warning: ScalyMUCK is running in debug mode! It will not handle mod errors too nicely.')
		return

	def parse_command(self, sender, input):
		data = string.split(input, ' ')
		command = string.lower(data[0])

		#if (intercept_input is False):
		if (self._command_entries.has_key(command)):
			function = self._command_entries[command]['Command']
			arguments = {
				'Sender': sender,
				'World': self._world_instance,
				'Arguments': data[1:len(data)],
				'Input': input[len(command)+1:],
			}
			# Debug mode allows for unsafe execution of mod crap so that we can purposely crash the game and get a verbose error
			if (self._debug_mode):
				function(arguments)
			else:
				try:
					function(arguments)
				except:
					connection.send('An internal error has occurred when running the command. Please contact your server administrator about the modification "' + self.command_entries[command]['Mod'] +'".\n')
					self.logger.write(strftime('%a, %d %b %Y %H:%M:%S: Command "' + command + '" in mod "' + self.command_entries[command]['Mod'] + '" invoked by user ' + connection.player.display_name + ' failed.'))
		else:
			connection.send('I do not know what it is to "' + command + '"\n')

		return

	def execute_callback(self, callback, client, input):
		return

	
