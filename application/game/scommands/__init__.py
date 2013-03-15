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

import edit

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

world=None

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

def command_dig(**kwargs):
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: dig <Room Name>')
		return

	sender = kwargs['sender']
	args = kwargs['arguments']

	room = world.create_room(input, '<Unset>', sender)
	sender.send('Room created. ID: ' + str(room.id))
	return

def command_teleport(**kwargs):
	args = kwargs['arguments']
	if (len(args) < 1):
		sender.send('Usage: teleport <Room ID|User Name>')
		return

	sender = kwargs['sender']

	input = args[0]
	target_room = world.find_room(id=input)
	if (target_room is not None):
		sender.location.broadcast(sender.display_name + ' fades into a mist and vanishes ...', sender)
		sender.send('The world around you slowly fades away ...')

		sender.set_location(target_room)
		sender.location.broadcast('A mist appears and forms into ' + sender.display_name + '.', sender)

		command_look(sender=sender, world=world)
		return

	sender.send('Unknown room.')
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

def command_edit(**kwargs):
	sender = kwargs['sender']
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: edit <object name>')
		return

	target = None
	lower = string.lower(input)
	if (lower == 'here'):
		target = sender.location
		if (target.owner_id != sender.id and sender.is_owner is False):
			sender.send('You do not own that.')
			return

	elif (lower == 'self'):
		target = sender

	if (target is not None):
		sender.is_editing = True
		sender.edit_target = target
		arguments['Menu'] = 'Main'
		edit.display_menu(arguments)
		arguments['Menu'] = 'EditMain'
		edit.display_menu(arguments)
	else:
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

def command_craft(**kwargs):
	sender = kwargs['sender']
	input = kwargs['input']

	if (input == ''):
		sender.send('Usage: craft <new item name>')
		return

	item = world.create_item(input, '<Unset>', sender, sender.inventory)
	sender.send('Item crafted.')

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

# Callbacks
def callback_client_authenticated(trigger, sender):
	sender.is_editing = False
	sender.edit_target = None
	sender.edit_menu = 'EditMain'

	command_look(sender=sender)
	return

def callback_message_sent(trigger, sender, input):
	if (sender.is_editing):
		edit.receive_input(sender, input)
		return True

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
	return

def get_commands():
	command_dict = {
		'say': 
		{ 
			'Command': command_say,
			'Description': 'Makes you say something. Only visible to the current room you\'re in.'
		},


		'pose': 
		{
			'Command': command_pose,
			'Description': 'Used to show arbitrary action. Only visible to the current room you\'re in.'
		},

		'look': 
		{
			'Command': command_look,
			'Description': 'Get your bearings. Look around in the local area to see what you can see.'
		},
		
		'dig':
		{
			'Command': command_dig,
			'Description': 'Creates a room elsewhere and hands you the ID number.'
		},

		'teleport':
		{
			'Command': command_teleport,
			'Description': 'Teleports you elsewhere.'
		},

		'move':
		{
			'Command': command_move,
			'Description': 'Moves to a new location.'
		},

		'edit':
		{
			'Command': command_edit,
			'Description': 'Edit your possessions.'
		},

		'inventory':
		{
			'Command': command_inventory,
			'Description': 'View your inventory.'
		},

		'take':
		{
			'Command': command_take,
			'Description': 'Take an item from the current room.'
		},

		'passwd':
		{
			'Command': command_passwd,
			'Description': 'Changes your password.'
		},

		'craft':
		{
			'Command': command_craft,
			'Description': 'Creates a new item.'
		},

		'drop':
		{
			'Command': command_drop,
			'Description': 'Drops an item from your inventory.'
		}
	}
	return command_dict
