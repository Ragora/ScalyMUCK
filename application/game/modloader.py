"""
	Modification loader class code for ScalyMUCK. This class
	is used to store and track loaded modifications that
	are in use by the server application

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import logging
import inspect
import importlib

import settings

logger = logging.getLogger('Mods')
class ModLoader:
	""" Mod loading class for ScalyMUCK. """
	workdir = None
	world = None
	interface = None
	session = None
	permissions = None
	commands = { }
	modifications = { }

	def __init__(self, world=None, interface=None, session=None, workdir=None, permissions=None):
		""" Initializes an instance of the ScalyMUCK mod loader. 

		There are several keyword arguments that should be used with this __init__ command:
			* world -- An instance of the game.World object to be used with this ModLoader.
			* interface -- An instance of the game.Interface object to be used with this ModLoader.
			* session -- An active database session from SQLAlchemy to be used with this ModLoader.
			* workdir -- The work directory of the current running application.
			* permissions -- An instance of the game.Permissions object to be used with this ModLoader.

		"""
		self.workdir = workdir
		self.world = world
		self.interface = interface
		self.session = session
		self.permissions = permissions
		self.set_defaults()

	def load(self, modifications):
		""" Loads a semicolon deliminated list of modifications from application/game.

		If any of the specified modifications happen to already be loaded into ScalyMUCK,
		they are merely reloaded so that any changes made since the last load will be applied
		and take affect.

		NOTE:
			If there happens to be a low-level Python error (IE: SyntaxError) then the server
			application will merely crash as of the moment. Same goes for any internal errors in a mod
			code base that happen to raise an exception that is not derived from one of the exception
			classes in game.Exception.

		"""
		for mod_name in modifications.split(';'):
			mod_name = mod_name.lower()
			if (mod_name in self.modifications):
				# Reloads the modification
				module = self.modifications[mod_name]
				modules = inspect.getmembers(module, inspect.ismodule)
				for name, sub_module in modules:
					reload(sub_module)
				module = reload(module)
				modification = module.Modification(config=self.config, world=self.world, interface=self.interface, session=self.session, permissions=self.permissions, modloader=self)
				self.modifications[mod_name] = (instance, module)
			else:
				try:
					module = importlib.import_module('game.%s' % (mod_name))
				except ImportError as e:
					self.logger.warning(str(e))
					return False
				else:
					config = settings.Settings('%s/config/%s.cfg' % (self.workdir, mod_name))

					modification = module.Modification(config=config, world=self.world, interface=self.interface, session=self.session, permissions=self.permissions, modloader=self)
					self.modifications.setdefault(mod_name, (modification, module))
					commands = modification.get_commands()
				logger.info('Processed modification %s.' % (mod_name))

			# Process aliases first
			aliases = { }
			for command in commands:
				for alias in commands[command]['aliases']:
					aliases.setdefault(alias, commands[command])
			commands.update(aliases)
			# Then process the dictionary
			for command in commands:
				commands[command]['modification'] = mod_name
				if (command in self.commands):
					logger.warn('Overlapping command definitions for command "%s"! %s -> %s' % (command, mod_name, self.commands[command]['modification']))
			self.commands.update(commands)
			self.set_defaults()

		return True

	def set_defaults(self):
		""" This command merely makes sure that the core commands are loaded. 

		It should be called everytime a modification is loaded in order to guarantee
		that a modification doesn't attempt to overwrite the core commands, even though
		by standard they shouldn't be defining these commands in the first place.

		"""
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

	def find_command(self, name):
		""" Returns a command by name. """
		if (name not in self.commands):
			return None
		else:
			return self.commands[name]

	# CORE Commands
	def command_mods(self, **kwargs):
		""" Internal command to list installed mods. """
		sender = kwargs['sender']
		loaded = ''
		sender.send('Loaded modifications: ')
		for key in self.modifications.keys():
			loaded += '%s, ' % (key)
		sender.send(loaded.rstrip(', '))

	def command_load(self, **kwargs):
		""" Internal command to load mods. """
		sender = kwargs['sender']
		input = kwargs['input'].lower()
		if (input.strip() == ' '):
			sender.send('No input.')

		if (self.load(input) is False):
			sender.send('Failed to load mod "%s".' % (input))
		else:
			sender.send('Loaded mod "%s".' % (input))

	def command_unload(self, **kwargs):
		""" Internal command to unload mods. """
		sender = kwargs['sender']
		input = kwargs['input'].lower()
		if (input in self.modifications):
			instance, module = self.modifications[input]
			self.modifications.pop(input)
			commands = instance.get_commands()
			for command in commands.keys():
				self.commands.pop(command)
			sender.send('Mod "%s" unloaded.' % (input))
		else:
			sender.send('Unknown modification.')