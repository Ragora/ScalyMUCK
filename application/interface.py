"""
	interface.py

	Basically the user interface for ScalyMUCK.
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string
import logging

from game import exception

class Interface:
	logger = None
	debug_mode = False
	world_instance = None
	command_entries = { }
	callback_entries = {
		'onClientAuthenticated': [ ],
		'onClientConnected': [ ],
		'onMessageSent': [ ]
	}

	loaded_mods = [ ]

	def __init__(self, config):
		self.logger = logging.getLogger('Mods')

		mod_list = string.split(config.get_index('LoadedMods', str), ';')
		for mod in mod_list:
			try:
				module = __import__('game.' + mod, globals(), locals(), [''], -1)
			except ImportError as e:
				self.logger.warning(str(e))
			else:
				commands = module.get_commands()
				if (commands is not None):
					for command in commands:
						self.command_entries[command] = commands[command]
						self.command_entries[command]['Mod'] = mod

				callbacks = module.get_callbacks()
				if (callbacks is not None):
					for callback in callbacks:
						if (callback in self.callback_entries):
							self.callback_entries[callback].append(callback)
						else:
							self.logger.warning('Loaded callback "%s" from modification "%s" but it is not used.', callback, mod)

		self.logger.warning('ScalyMUCK is running in debug mode! It will not handle mod errors too nicely.')
		return

	def parse_command(self, sender, input):
		data = string.split(input, ' ')
		command = string.lower(data[0])

		#if (intercept_input is False):
		if (self.command_entries.has_key(command)):
			function = self.command_entries[command]['Command']
			arguments = {
				'Sender': sender,
				'World': self.world_instance,
				'Arguments': data[1:len(data)],
				'Input': input[len(command)+1:],
			}
			try:
				function(arguments)
			except exception.ModApplicationError as e:
				print(e)
		else:
			# This is done because apparently when in the terminal, you can send keycodes and blow up the server
			try:
				sender.send('I do not know what it is to "' + command + '".')
			except UnicodeDecodeError as e:
				sender.send('I do not know what it is to do that.')

		return

	def execute_callback(self, callback, client, input):
		return

	
