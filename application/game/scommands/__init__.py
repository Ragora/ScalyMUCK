"""
	ScalyMUCK Normal Commands
	This mod code is simply ScalyMUCK's
	default user commands.

	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

from blinker import signal

server_version_major = 1
server_version_minor = 0
server_version_revision = 0

version_major = 1
version_minor = 0
version_revision = 0
name = 'ScalyMUCK Commands'
description = 'This modification implements various normal MU* commands into ScalyMUCK.'
copyright = 'Copyright (c) 2013 Liukcairo'
author = 'Liukcairo'

world = None
interface = None

work_factor = 10

# Commands
def command_say(**kwargs):
	sender = kwargs['sender']
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: say <message>')
		return

	sender.location.broadcast(sender.display_name + ' says, "' + input + '"', sender)
	sender.send('You say, "' + input + '"')
	return

def command_pose(**kwargs):
	sender = kwargs['sender']
	sender.location.broadcast(sender.display_name + ' ' + kwargs['input'])
	return

def command_look(**kwargs):
	sender = kwargs['sender']
	room = sender.location
	
	sender.send('<' + room.name + '>')
	sender.send('Obvious Exits: ')
	if (len(room.exits) != 0):
		for exit in room.exits:
			sender.send('	' + exit.name)
	else:
		sender.send('	None')

	sender.send('People: ')
	for player in room.players:
		sender.send('	' + player.display_name)
	sender.send('Items: ')

	if (len(room.items) != 0):
		for item in room.items:
			sender.send('	' + item.name)
	else:
		sender.send('	None')

	sender.send('Description:')
	sender.send(room.description)
	return

def command_move(**kwargs):
	sender = kwargs['sender']
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: move <name of exit>')
		return

	for exit in sender.location.exits:
		if (string.lower(exit.name) == string.lower(input)):
			sender.send('You move out.')
			sender.location.broadcast(sender.display_name + ' exits the room.', sender)
			sender.set_location(exit.target_id)
			sender.location.broadcast(sender.display_name + ' enters the room.', sender)
			command_look(sender=sender, world=kwargs['world'])
			return

	sender.send('I do not see that.')
	return

def command_inventory(**kwargs):
	sender = kwargs['sender']

	sender.send('Items:')
	if (len(sender.inventory.items) != 0):
		for item in sender.inventory.items:
			sender.send('	' + item.name)
	else:
		sender.send('	None')

	# Pocket dimension anybody?
	if (len(sender.inventory.players) != 0):
		sender.send('People: ')
		for player in sender.inventory.players:
			sender.send('	' + player.display_name)
	return

def command_take(**kwargs):
	sender = kwargs['sender']
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: take <object name>')
		return

	for item in sender.location.items:
		if (item.name == input):
			sender.send('Taken.')
			item.set_location(sender.inventory)
			return

	sender.send('I do not see that.')

def command_passwd(**kwargs):
	sender = kwargs['sender']
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: passwd <password>')
		return

	sender.set_password(input)
	sender.send('Your password has been changed. Remember it well.')

def command_drop(**kwargs):
	sender = kwargs['sender']
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: drop <item name>')
		return

	for item in sender.inventory.items:
		if (item.name == input):
			sender.send('You dropped that item.')
			sender.location.broadcast(sender.display_name + ' drops a/an ' + item.name + '.', sender)
			item.set_location(sender.location)
			return
	sender.send('I see no such item.')

def command_help(**kwargs):
	sender = kwargs['sender']
	input = string.lower(kwargs['input'])

	if (input not in interface.commands):
		sender.send('For more information, type: help <command>')
		sender.send('Command listing: ')
		out = ''
		for command in interface.commands:
			out += command + ', '
		# Cheap trick to strip off the last comma (and space) but eh!
		sender.send(out[:len(out)-2]) 
		return
	else:
		sender.send('From: ' + interface.commands[input]['mod'])
		sender.send('Usage: ' + interface.commands[input]['usage'])
		sender.send(interface.commands[input]['description'])

def command_quit(**kwargs):
	sender = kwargs['sender']
	sender.disconnect()

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
		if (target is sender):
			sender.send('That is yourself!')
			return
		elif (target.is_sadmin ==1 or target.is_owner == 1):
			sender.send('You cannot do that, they are too powerful.')
			return

		item = world.create_item(target.display_name, target.description, sender, sender.inventory)
		sender.send('User "' + target.display_name + '" frogged. Check your inventory.')
		target.send(sender.display_name + ' has turned you into a small plastic figurine, never to move again and discreetly places you in their inventory.')
		sender.location.broadcast(sender.display_name + ' has turned ' + target.display_name + ' into a small plastic figurine, never to move again.', sender, target)
		target.delete()
	else:
		sender.send('User "' + name + '" does not exist anywhere.')

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
	player = world.create_player(name, password, work_factor, sender.location)
	sender.send('User "' + name + '" created.')

def command_admin(**kwargs):
	sender = kwargs['sender']
	if (sender.is_admin is False):
		sender.send('You are not magical enough.')
		return

	args = kwargs['arguments']
	if (len(args) < 1):
		sender.send('Usage: admin <name>')
		return

	name = args[0]

	target = world.find_player(name=string.lower(name))
	if (target is not None):
		if (target is sender):
			sender.send('That is yourself!')
			return
		elif (sender.check_admin_trump(target) is False):
			sender.send('You cannot do that. They are too strong.')
			target.send(sender.display_name + ' tried to take your administrator privileges away.')
			return

		target.set_is_admin(target.is_admin is False)
		if (target.is_admin == 0):
			sender.send(target.display_name + ' is no longer an administrator.')
			target.send(sender.display_name + ' took your adminship.')
		else:
			sender.send(target.display_name + ' is now an administrator.')
			target.send(sender.display_name + ' gave you adminship rights.')
		return
	sender.send('Unknown user.')

def command_sadmin(**kwargs):
	sender = kwargs['sender']
	if (sender.is_sadmin is False):
		sender.send('You are not magical enough.')
		return

	args = kwargs['arguments']
	if (len(args) < 1):
		sender.send('Usage: sadmin <name>')
		return

	name = args[0]

	target = world.find_player(name=string.lower(name))
	if (target is not None):
		if (target is sender):
			sender.send('That is yourself!')
			return
		elif (sender.check_admin_trump(target) is False):
			sender.send('You cannot do that. They are too strong.')
			target.send(sender.display_name + ' tried to take your super administrator privileges away.')
			return

		target.set_is_super_admin(target.is_sadmin is False)
		if (target.is_sadmin is False):
			sender.send(target.display_name + ' is no longer a super administrator.')
			target.send(sender.display_name + ' took your super adminship.')
		else:
			sender.send(target.display_name + ' is now a super administrator.')
			target.send(sender.display_name + ' gave you super adminship rights.')
		return
	sender.send('Unknown user.')

def command_chown(**kwargs):
	sender = kwargs['sender']
	args = kwargs['arguments']

	if (len(args) < 2):
		sender.send('Usage: chown <item name> <new owner>')
		return

	item_name = args[0]
	owner_name = args[1]

# Callbacks
def callback_client_authenticated(trigger, sender):
	command_look(sender=sender)
	return

def callback_message_sent(trigger, sender, input):
	if (len(input) != 0):
		# TODO: Make this not suck
		if (input[0:2] == ': '):
			command_pose(sender=sender, input=input[2:])
			return True
		elif (input[0] == ':'):		
			command_pose(sender=sender, input=input[1:])
			return True

		if (input[0:2] == '" '):
			command_say(sender=sender, input=input[2:])
			return True
		elif (input[0] == '"'):
			command_say(sender=sender, input=input[1:])
			return True

	return False

# Function calls
def initialize(config):
	signal('post_client_authenticated').connect(callback_client_authenticated)
	signal('pre_message_sent').connect(callback_message_sent)
	work_factor = config.get_index('WorkFactor', int)
	return

def get_commands():
	command_dict = {
		'say': 
		{ 
			'command': command_say,
			'description': 'Makes you say something. Only visible to the current room you\'re in.',
			'usage': 'say <arbitrary text> | "<arbitrary text>',
			'aliases': [ 'speak' ]
		},

		'pose': 
		{
			'command': command_pose,
			'description': 'Used to show arbitrary action. Only visible to the current room you\'re in.',
			'usage': 'pose <arbitrary pose> | :<arbitrary pose>'
			'aliases': [ ]
		},

		'look': 
		{
			'command': command_look,
			'description': 'Get your bearings. Look around in the local area to see what you can see.',
			'usage': 'look [room name | item name | player name]'
			'aliases': [ ]
		},
		
		'move':
		{
			'command': command_move,
			'description': 'Moves to a new location.',
			'usage': 'move <exit name>'
			'aliases': [ 'go' ]
		},

		'inventory':
		{
			'command': command_inventory,
			'description': 'View your inventory.',
			'usage': 'inventory'
			'aliases': [ ]
		},

		'take':
		{
			'command': command_take,
			'description': 'Take an item from the current room.',
			'usage': 'take <item>'
			'aliases': [ ]
		},

		'passwd':
		{
			'command': command_passwd,
			'description': 'Changes your password.',
			'usage': 'passwd <new password>'
			'aliases': [ ]
		},

		'drop':
		{
			'command': command_drop,
			'description': 'Drops an item from your inventory.',
			'usage': 'drop <item name>'
			'aliases': [ ]
		},

		'help':
		{
			'command': command_help,
			'description': 'Displays the help text.',
			'usage': 'help [command name]'
			'aliases': [ ]
		},

		'quit':
		{
			'command': command_quit,
			'description': 'Drops your connection from the server.',
			'usage': 'quit'
			'aliases': [ 'leave' ]
		},

		'frog':
		{
			'command': command_froguser,
			'description': 'Super Admin only: Deletes a user from the world -- making them an item in your inventory to with as you please.',
			'usage': 'frog <player name>'
			'aliases': [ ]
		},

		'adduser':
		{
			'command': command_adduser,
			'description': 'Creates a new player in the world.',
			'usage': 'adduser <name> <password>'
			'aliases': [ ]
		},

		'admin':
		{
			'command': command_admin,
			'description': 'Admin only: Toggles the admin status of a specified player.',
			'usage': 'admin <name>'
			'aliases': [ ]
		},

		'sadmin':
		{
			'command': command_sadmin,
			'description': 'Super Admin only: Toggles the super admin status of a specified player.',
			'usage': 'sadmin <name>'
			'aliases': [ ]
		},

		'chown':
		{
			'command': command_chown,
			'description': 'Transfers ownership of an item in your inventory or in the room to a specified player providied you are the original owner.',
			'usage': 'chown <item name> <new owner name>'
			'aliases': [ ]
		}
	}
	return command_dict
