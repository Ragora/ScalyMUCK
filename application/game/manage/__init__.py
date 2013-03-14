"""
      ScalyMUCK management plugin.
"""

import string

server_version_major = 1
server_version_minor = 0
server_version_revision = 0

version_major = 1
version_minor = 0
version_revision = 0
name = 'ScalyMUCK Management'
description = 'Provides ingame commands to manage the server.'
copyright = 'Copyright (c) 2013 Liukcairo'
author = 'Liukcairo'

world=None

# Commands
def command_adduser(**kwargs):
	sender = kwargs['sender']
	if (sender.is_sadmin is False):
		sender.send('You are not magical enough.')
		return

	args = kwargs['arguments']
	if (len(args) < 2):
		sender.send('Usage: adduser <name> <password>')
		return

	name = args[0]
	password = args[1]

	if (world.find_player(name=string.lower(name)) is not None):
		sender.send('User already exists.')
		return

	# TODO: Make this take server prefs into consideration, and also let this have a default location ...
	player = world.create_player(name, password, 10, sender.location)
	sender.send('User "' + name + '" created.')

def command_froguser(**kwargs):
	sender = kwargs['sender']
	if (sender.is_sadmin is False):
		sender.send('You are not magical enough.')
		return

	args = kwargs['arguments']
	if (len(args) < 1):
		sender.send('Usage: frog <name>')
		return

	name = args[0]
	target = world.find_player(name=string.lower(name))
	if (target is not None):
		item = world.create_item(target.display_name, target.description, sender, sender.inventory)
		sender.send('User "' + target.display_name + '" frogged. Check your inventory.')
		target.send(sender.display_name + ' has turned you into a small plastic figurine, never to move again and discreetly places you in their inventory.')
		sender.location.broadcast(sender.display_name + ' has turned ' + target.display_name + ' into a small plastic figurine, never to move again.', sender, target)
		target.delete()
	else:
		sender.send('User "' + name + '" does not exist anywhere.')

def initialize(config):
	return

def get_commands():
	command_dict = {
		'adduser': 
		{ 
			'Command': command_adduser,
			'Description': 'Adds a new user to the world. Usage: adduser <name> <password>'
		},
		'frog':
		{
			'Command': command_froguser,
			'Description': 'Deletes the specified user from the world and turning them into an item.'
		},
	}
	return command_dict

def get_callbacks():
	return None
