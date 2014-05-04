"""
	Modification loader class code for ScalyMUCK. This class
	is used to store and track loaded modifications that
	are in use by the server application

	This software is licensed under the MIT license.
	Please refer to LICENSE.txt for more information.
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
	initialized = False
	commands = { }
	""" A dictionary of all loaded commands. The keys are the actual name a command is referred to by and said keys point to
	Python functions to be called upon use. """
	modifications = { }
	""" A dictionary of all loaded modifications. The keys are the internal name of the mod and each key refers to a tuple
	with the following format: (instance, module). """

	def initialize(self, **kwargs):
		self.workdir = kwargs['workdir']
		self.world = kwargs['world']
		self.interface = kwargs['interface']
		self.session = kwargs['session']
		self.permissions = kwargs['permissions']
		self.set_defaults()

		for modification_name in self.modifications.keys():
			modification_instance, module = self.modifications[modification_name]
			modification_instance.initialize(**kwargs)

		self.initialized = True

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
				modification, module = self.modifications[mod_name]
				modules = inspect.getmembers(module, inspect.ismodule)
				for name, sub_module in modules:
					reload(sub_module)
				module = reload(module)
				config = settings.Settings('%s/config/%s.cfg' % (self.workdir, mod_name))
				instance = module.Modification()
				self.modifications[mod_name] = (instance, module)
			else:
				try:
					module = importlib.import_module('game.%s' % (mod_name))
				except ImportError as e:
					logger.warning(str(e))
					return False
				else:
					config = settings.Settings('%s/config/%s.cfg' % (self.workdir, mod_name))

					modification = module.Modification()
					if (self.initialized):
						modification.initialize(world=self.world, config=config, session=self.session, permissions=self.permissions, interface=self.interface, modloader=self)
					self.modifications.setdefault(mod_name, (modification, module))

				logger.info('Processed modification %s.' % (mod_name))

			# Process aliases first
			aliases = { }
			commands = modification.get_commands()
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
		self.commands['mods']['category'] = 'Core'

		self.commands['load'] = { }
		self.commands['load']['command'] = self.command_load
		self.commands['load']['description'] = 'Loads the specified mod.'
		self.commands['load']['usage'] = 'load <name>'
		self.commands['load']['privilege'] = 3
		self.commands['load']['modification'] = '<CORE>'
		self.commands['load']['category'] = 'Core'

		self.commands['unload'] = { }
		self.commands['unload']['command'] = self.command_unload
		self.commands['unload']['description'] = 'Unloads the specified mod.'
		self.commands['unload']['usage'] = 'unload <name>'
		self.commands['unload']['privilege'] = 3
		self.commands['unload']['modification'] = '<CORE>'
		self.commands['unload']['category'] = 'Core'

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
