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

from game import exception, settings

class Interface:
	logger = None
	debug_mode = False
	world = None
	commands = { }
	callbacks = {
		'onClientAuthenticated': [ ],
		'onClientConnected': [ ],
		'onMessageSent': [ ]
	}

	loaded_mods = [ ]

	def __init__(self, config, world):
		self.logger = logging.getLogger('Mods')
		self.world = world

		mod_list = string.split(config.get_index('LoadedMods', str), ';')
		for mod in mod_list:
			self.load_mod(mod)
		return

	def load_mod(self, mod):
		try:
			module = __import__('game.' + mod, globals(), locals(), [''], -1)
		except ImportError as e:
			self.logger.warning(str(e))
		else:
			mod_config = settings.Settings('config/' + mod + '.cfg')
			module.initialize(mod_config)
			mod_commands = module.get_commands()
			if (mod_commands is not None):
				for command in mod_commands:
					self.commands[command] = mod_commands[command]
					self.commands[command]['Mod'] = mod

			mod_callbacks = module.get_callbacks()
			if (mod_callbacks is not None):
				for callback in mod_callbacks:
					if (callback in self.callbacks):
						entry = { 'Command': mod_callbacks[callback], 'Mod': mod }
						self.callbacks[callback].append(entry)
					else:
						self.logger.warning('Loaded callback "%s" from modification "%s" but it is not used.', callback, mod)
		

	def parse_command(self, sender, input):
		intercept_input = self.execute_callback('onMessageSent', sender, input)

		data = string.split(input, ' ')
		command = string.lower(data[0])

		if (self.commands.has_key(command) and intercept_input is False):
			function = self.commands[command]['Command']
			arguments = {
				'Sender': sender,
				'World': self.world,
				'Arguments': data[1:len(data)],
				'Input': input[len(command)+1:],
			}
			try:
				function(arguments)
			except exception.ModApplicationError as e:
				line_one = 'An error has occurred within the modification "' + self.commands[command]['Mod'] + ' while executing the command.'
				line_two = 'Error Condition: '
				line_three = str(e)

				self.logger.error(line_one)
				self.logger.error(line_two)
				self.logger.error(line_three)
				sender.send(line_one)
				sender.send(line_two)
				sender.send(line_three)
				sender.send('Please report this incident to your server administrator immediately.')

		elif (intercept_input is False):
			# This is done because apparently when in the terminal, you can send keycodes and blow up the server
			try:
				sender.send('I do not know what it is to "' + command + '".')
			except UnicodeDecodeError as e:
				sender.send('I do not know what it is to do that.')

		return

	def execute_callback(self, callback, client, input):
		intercept = False
		if (callback in self.callbacks):
			data = {
				'Sender': client,
				'World': self.world,
				'Input': input
			}
			for entry in self.callbacks[callback]:
				function = entry['Command']
				try:
					if (intercept is False and function(data)):
						intercept = True
				except exception.ModApplicationError as e:
					line_one = 'An error has occurred within the modification "' + self.callbacks[callback]['Mod'] + ' while executing callback "' + callback + '".'
					line_two = 'Error Condition: '
					line_three = str(e)

					self.logger.error(line_one)
					self.logger.error(line_two)
					self.logger.error(line_three)
					sender.send(line_one)
					sender.send(line_two)
					sender.send(line_three)
					sender.send('Please report this incident to your server administrator immediately.')
		return intercept

	
