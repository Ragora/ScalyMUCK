"""
	fuzzball.py

	ScalyMUCK implementation of common Fuzzball
	commands.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

from blinker import signal

import game.models

class Modification:
	""" Main class object to load and initialize the fuzzball modification. """
	world = None
	interface = None
	session = None

	commands = None

	def __init__(self, **kwargs):
		self.config = kwargs['config']
		self.interface = kwargs['interface']
		self.session = kwargs['session']
		self.world = kwargs['world']

		self.commands = { 'dig': self.fuzz_command_dig,
				  'create': self.fuzz_command_create,
				  'desc': self.fuzz_command_desc				
		}

		signal('pre_message_sent').connect(self.callback_message_sent)

	# Callbacks
	def callback_message_sent(self, trigger, sender, input):
		if (len(input) < 2):
			sender.send('Invalid input.')
			return True
		elif (input[0] == '@'):
			space = input.find(' ')
			if (space == -1):
				command = input[1:].lower()
			else:
				command = input[1:space].lower()
			
			if (command in self.commands):
				function = self.commands[command]
				args = input[len(command)+2:]

				equals = args.find('=')
				if (equals != -1):
					function(sender=sender, input=args[equals+1:], preinput=args[:equals])
				else:
					function(sender=sender, input=args, preinput=None)
			else:
				sender.send('I do not know what it is to \'%s\'.' % (command))
			
			return True
		else:
			return False

	# Fuzzball Commands
	def fuzz_command_dig(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['input']
		preargs = kwargs['preinput']
		
		if (preargs is not None):
			args = preargs

		room = self.world.create_room(name=args, description='<Unset>', owner=sender)
		sender.send('%s created with room number %u.' % (args, room.id))

	def fuzz_command_desc(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['input']
		preargs = kwargs['preinput']

		if (preargs is None):
			sender.send('I don\'t see that here.')
		else:
			if (preargs == 'here'):
				target = sender.location
			else:
				target = sender.inventory.find_item(name=preargs)
				if (target is None):
					target = sender.location.find_item(name=preargs)
					if (target is None):
						sender.send('I don\'t see that here.')
						return

			target.set_description(args)
			sender.send('Description set.')

	def fuzz_command_create(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['input']
		preargs = kwargs['preinput']
		
		if (preargs is not None):
			args = preargs

		item = self.world.create_item(name=args, description='<Unset>', owner=sender, location=sender.inventory)
		sender.send('%s created with number %u.' % (args, item.id))

	def get_commands(self):
		command_dict = { }
		return command_dict
