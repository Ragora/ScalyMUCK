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

from blinker import signal

from game import exception, settings

class Interface:
	logger = None
	world = None
	mods = [ ]
	commands = { }
	
	pre_message = signal('pre_message_sent')
	post_message = signal('post_message_sent')

	def __init__(self, config, world):
		self.logger = logging.getLogger('Mods')
		self.world = world

		mod_list = string.split(config.get_index('LoadedMods', str), ';')
		for mod in mod_list:
			self.load_mod(mod, config)
		return

	def load_mod(self, mod, config):
		try:
			module = __import__('game.' + mod, globals(), locals(), [''], -1)
		except ImportError as e:
			self.logger.warning(str(e))
		else:
			config.load('config/' + mod + '.cfg')
			module.world = self.world
			module.interface = self
			module.initialize(config)
			self.mods.append(module)

			mod_commands = module.get_commands()
			for mod_command in mod_commands:
				self.commands[mod_command] = mod_commands[mod_command]
				self.commands[mod_command]['mod'] = mod

	def parse_command(self, sender, input):
		returns = self.pre_message.send(None, sender=sender, input=input)
		intercept_input = False
		for set in returns:
			if (set[1] is True):
				intercept_input = True
				break

		data = string.split(input, ' ')
		command = string.lower(data[0])

		if (intercept_input is False and command in self.commands):
			try:
				function = self.commands[command]['command']
				function(sender=sender, input=input[len(command)+1:], arguments=data[1:len(data)])
			except exception.ModApplicationError as e:
				line_one = 'An error has occurred while executing the command.'
				line_two = 'Error Condition: '
				line_three = str(e)

				self.logger.error(line_one)
				self.logger.error(line_two)
				self.logger.error(line_three)
				sender.send(line_one)
				sender.send(line_two)
				sender.send(line_three)
				sender.send('Please report this incident to your server administrator immediately.')

		elif (intercept_input is False and command != ''):
			# This is done because apparently when in the terminal, you can send keycodes and blow up the server
			try:
				sender.send('I do not know what it is to "' + command + '".')
			except UnicodeDecodeError as e:
				sender.send('I do not know what it is to do that.')

		self.post_message.send(None, sender=sender, input=input)

	
