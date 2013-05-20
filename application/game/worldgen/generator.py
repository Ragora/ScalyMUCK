"""
	generator.py

	World generation implementation. Play God, little
	monkey.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

from blinker import signal

import game.models

class Modification:
	""" Main class object to load and initialize the generator plugin. """
	world = None
	interface = None
	data = { }

	def __init__(self, **kwargs):
		self.world = kwargs['world']
		self.interface = kwargs['interface']

		signal('post_client_authenticated').connect(self.callback_client_authenticated)
		signal('pre_client_disconnect').connect(self.callback_client_disconnected)

	# Configuration Page
	def generate_display(self, sender):
		if (self.data[sender.id]['page'] == 'main'):
			return
		return

	# Commands
	def command_generate(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['arguments']

	# Callbacks
	def callback_client_authenticated(self, trigger, sender):
		self.data.setdefault(sender.id, {})
		self.data[sender.id].setdefault('page', 'main')

	def callback_client_disconnected(self, trigger, sender):
		self.data.pop(sender.id) # Throws the data out of the U.S.S. Scope and gets it garbage collected.

	def get_commands(self):
		command_dict = {
			'generate': 
			{ 
				'command': self.command_generate,
				'description': 'Creator of worlds, O\' mighty one.',
				'usage': 'generate <param>',
				'aliases': [ ],
				'privilege': 2
			},
		}
