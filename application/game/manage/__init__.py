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

# Commands
def command_adduser(arguments):
	sender = arguments['Sender']
	if (sender.is_sadmin is False):
		sender.send('You are not magical enough.')
		return

	args = arguments['Arguments']
	if (len(args) < 2):
		sender.send('Usage: adduser <name> <password>')
		return

	name = args[0]
	password = args[1]

	world = arguments['World']
	if (world.find_player(name=string.lower(name)) is not None):
		sender.send('User already exists.')
		return

	# TODO: Make this take server prefs into consideration, and also let this have a default location ...
	player = world.create_player(name, password, 10, sender.location)
	sender.send('User "' + name + '" created.')

def command_froguser(arguments):
	sender = arguments['Sender']
	if (sender.is_sadmin is False):
		sender.send('You are not magical enough.')
		return

	args = arguments['Arguments']
	if (len(args) < 1):
		sender.send('Usage: frog <name>')
		return

	name = args[0]
	world = arguments['World']
	if (world.find_player(name=string.lower(name)) is not None):
		sender.send('User "' + name + '" frogged.')
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
