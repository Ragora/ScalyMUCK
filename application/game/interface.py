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
import importlib
import inspect

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
	config = None
	session = None
	server = None
	mods = [ ]
	commands = { }
	workdir = ''
	
	pre_message = signal('pre_message_sent')
	post_message = signal('post_message_sent')

	def __init__(self, config=None, world=None, workdir='', session=None, server=None):
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
			session -- A working session object that points to the active database.
			server -- The very instance of the ScalyMUCK server.

		"""
		self.logger = logging.getLogger('Mods')
		self.world = world
		self.workdir = workdir
		self.config = config
		self.session = session
		self.server = server

		# Implement the default commands.
		self.commands['mods'] = { }
		self.commands['mods']['command'] = self.command_mods
		self.commands['mods']['description'] = 'Lists all loaded mods.'
		self.commands['mods']['usage'] = 'mods'
		self.commands['mods']['privilege'] = 3
		self.commands['mods']['modification'] = '<CORE>'

		self.commands['load'] = { }
		self.commands['load']['command'] = self.command_load
		self.commands['load']['description'] = 'Loads the specified mod.'
		self.commands['load']['usage'] = 'load <name>'
		self.commands['load']['privilege'] = 3
		self.commands['load']['modification'] = '<CORE>'

		self.commands['unload'] = { }
		self.commands['unload']['command'] = self.command_unload
		self.commands['unload']['description'] = 'Unloads the specified mod.'
		self.commands['unload']['usage'] = 'unload <name>'
		self.commands['unload']['privilege'] = 3
		self.commands['unload']['modification'] = '<CORE>'

		# Iterate through our loaded mods and actually load them
		mods = string.split(config.get_index('LoadedMods', str), ';')
		for mod in mods:
			self.load_mod(name=mod)
		return

	def load_mod(self, name=None):
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
			connection -- A working connection object that points to the active database.

		"""
		name = name.lower()
		for index, group in enumerate(self.mods):
			mod_name, module, mod_instance = group
			if (mod_name == name):
				# Reload the mod in all of its entirety
				modules = inspect.getmembers(module, inspect.ismodule)
				for name, sub_module in modules:
					reload(sub_module)
				module = reload(module)

				modification = module.Modification(config=self.config, world=self.world, interface=self, session=self.session)
				commands = modification.get_commands()
				for command in commands:
					commands[command]['modification'] = mod_name
				self.commands.update(commands)
				self.mods[index] = (mod_name, module, modification)
				return

		try:
			module = importlib.import_module('game.%s' % (name))
		except ImportError as e:
			self.logger.warning(str(e))
		else:
			if (self.config is not None):
				self.config.load('%s/config/%s.cfg' % (self.workdir, name))

			modification = module.Modification(config=self.config, world=self.world, interface=self, session=self.session)
			self.mods.append((name, module, modification))

			commands = modification.get_commands()
			# Process aliases first
			aliases = { }
			for command in commands:
				for alias in commands[command]['aliases']:
					aliases.setdefault(alias, commands[command])
			commands.update(aliases)
			# Then process the dictionary
			for command in commands:
				commands[command]['modification'] = name
				if (command in self.commands):
					self.logger.warn('Overlapping command definitions for command %s! %s -> %s' % (command, name, self.commands[command][modification]))
			self.commands.update(commands)

	def parse_command(self, sender=None, input=None):
		""" Called internally by the ScalyMUCK server.

		When a user sends a string of data to the server for processing and have passed
		the initial authentification stage, that string of data is passed in here by the
		server for processing. This function is what actually performs the command lookups
		in the loaded command database.

		Keyword arguments:
			sender -- The instance of Player that has trying to invoke a command.
			input -- The text that the Player happened to send.

		"""
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
				privilege = self.commands[command]['privilege']
				if (privilege == 1 and sender.is_admin is False):
					sender.send('You must be an administrator.')
					return
				elif (privilege == 2 and sender.is_sadmin is False):
					sender.send('You must be a super administrator.')
					return
				elif (privilege == 3 and sender.is_owner is False):
					sender.send('You must be the owner of the server.')
					return

				# You're not trying to do something you shouldn't be? Good.
				function = self.commands[command]['command']
				function(sender=sender, input=input[len(command)+1:], arguments=data[1:len(data)])
			except exception.ModApplicationError as e:
				line_one = 'An error has occurred while executing the command: %s' % (command)
				line_two = 'From modification: %s' % (self.commands[command]['modification'])
				line_three = 'Error Condition: '
				line_four = str(e)

				self.logger.error(line_one)
				self.logger.error(line_two)
				self.logger.error(line_three)
				self.logger.error(line_four)
				sender.send(line_one)
				sender.send(line_two)
				sender.send(line_three)
				sender.send(line_four)
				sender.send('Please report this incident to your server administrator immediately.')

		elif (intercept_input is False and command != ''):
			sender.send('I do not know what it is to "%s".' % (command))

		self.post_message.send(None, sender=sender, input=input)

	def command_mods(self, **kwargs):
		""" Internal command to list installed mods. """
		sender = kwargs['sender']
		loaded = ''
		for group in self.mods:
			mod_name, module, mod_instance = group
			loaded += mod_name + ', '
		sender.send(loaded.rstrip(', '))

	def command_load(self, **kwargs):
		""" Internal command to load mods. """
		sender = kwargs['sender']
		input = kwargs['input'].lower()
		for group in self.mods:
			mod_name, module, mod_instance = group
			if (input == mod_name):
				self.load_mod(input)
				sender.send('Mod "%s" reloaded.' % (input))
				return
		self.load_mod(input)
		sender.send('Attempted to load mod "%s".' % (input))

	def command_unload(self, **kwargs):
		""" Internal command to unload mods. """
		sender = kwargs['sender']
		input = kwargs['input'].lower()
		for index, group in enumerate(self.mods):
			mod_name, module, mod_instance = group
			if (input == mod_name):
				self.mods.pop(index)
				commands = mod_instance.get_commands()
				for command in commands:
					self.commands.pop(command)
				sender.send('Mod "%s" unloaded.' % (input))
				return
		sender.send('Unknown mod.')
