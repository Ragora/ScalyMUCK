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
	""" Client-Server interface class.

	The interface class is exactly how it sounds; it's what the users interact
	with directly when connected to the ScalyMUCK server, with an exception being 
	the login screen for simplicity and security.

	"""
	logger = None
	world = None
	mods = [ ]
	commands = { }
	workdir = ''
	
	pre_message = signal('pre_message_sent')
	post_message = signal('post_message_sent')

	""" Initializes an instance of the ScalyMUCK Client-Server interface class.

	The interface class is created internallu by the ScalyMUCK server.

	The server passes in an active instance of game.Settings and game.World
	for the interface to talk to when loading mods as the configuration is 
	used to load relevant config files for the mods and is passed in while
	the instance of game.World is assigned to each module so that they may
	access the game world.

	Keyword arguments:
		config -- An instance of Settings that is to be used to load relevant configuration data.
		world -- An instance of the World to pass over to every initialized modification.
		workdir -- The current working directory of the application. This should be an absolute path to application/.

	"""
	def __init__(self, config=None, world=None, workdir=''):
		self.logger = logging.getLogger('Mods')
		self.world = world
		self.workdir = workdir

		mods = string.split(config.get_index('LoadedMods', str), ';')
		for mod in mods:
			self.load_mod(name=mod, config=config)
		return

	""" Loads the specified modification from the "game" folder.

	Modifications are loaded from the application/game folder of ScalyMUCK,
	they are basically just normal Python modules that are imported and have
	a special function call to load the commands. See the URL below for information:
	http://dx.no-ip.org/doku/doku.php/projects:scalymuck:modapi:examplemod

	The config argument is meant to be an instance of game.Settings so that the interface
	can load the modification's configuration file and pass in the loading data to the mod's
	initialize function.

	Keyword arguments:
		name -- The name of the mod to attempt to load.
		config -- An instance of Settings that is to be used to load relevant configuration data.

	"""
	def load_mod(self, name=None, config=None):
		try:
			module = __import__('game.' + name, globals(), locals(), [''], -1)
		except ImportError as e:
			self.logger.warning(str(e))
		else:
			if (config is not None):
				config.load(self.workdir + '/config/' + name + '.cfg')

			module.world = self.world
			module.interface = self
			module.initialize(config)
			self.mods.append(module)

			commands = module.get_commands()
			self.commands.update(commands)

	""" Called internally by the ScalyMUCK server.

	When a user sends a string of data to the server for processing and have passed
	the initial authentification stage, that string of data is passed in here by the
	server for processing. This function is what actually performs the command lookups
	in the loaded command database.

	Keyword arguments:
		sender -- The instance of Player that has trying to invoke a command.
		input -- The text that the Player happened to send.

	"""
	def parse_command(self, sender=None, input=None):
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
