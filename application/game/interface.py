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

import modloader
import permissions
from game import exception, settings

logger = logging.getLogger('Mods')
class Interface:
	""" Client-Server interface class.

	The interface class is exactly how it sounds; it's what the users interact
	with directly when connected to the ScalyMUCK server, with an exception being 
	the login screen for simplicity and security.

	"""
	world = None
	config = None
	session = None
	server = None
	permissions = None
	workdir = ''
	modloader = None
	
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
		self.permissions = permissions.Permissions(workdir=workdir)
		self.modloader = modloader.ModLoader(world=world, interface=self, session=session, workdir=workdir, permissions=self.permissions)
		self.modloader.load(config.get_index('LoadedMods', str))

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
		command_data = self.modloader.find_command(command)
		if (intercept_input is False and command_data is not None):
			try:
				privilege = command_data['privilege']
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
				command_func = command_data['command']
				command_func(sender=sender, input=input[len(command)+1:], arguments=data[1:len(data)])
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
