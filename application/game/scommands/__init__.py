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

# Commands
def command_say(arguments):
	sender = arguments['Sender']
	input = arguments['Input']
	room = sender.location

	if (input == ''):
		sender.send('Usage: say <message>')
		return

	for player in room.players:
		if (player != sender):
			player.send(sender.display_name + ' says, "' + input + '"')

	sender.send('You say, "' + input + '"')
	return

def command_pose(arguments):
	sender = arguments['Sender']
	input = arguments['Input']
	room = sender.location

	for player in room.players:
		player.send(sender.display_name + ' ' + input)
	return

def command_look(arguments):
	sender = arguments['Sender']
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
			sender.send(item.name)
	else:
		sender.send('	None')

	sender.send('Description:')
	sender.send(room.description)
	return

def command_dig(arguments):
	sender = arguments['Sender']
	args = arguments['Arguments']
	world = arguments['World']
	input = arguments['Input']

	if (input == ''):
		sender.send('Usage: dig <Room Name>')
		return

	room = world.create_room(input, '<Unset>', sender)
	sender.send('Room created. ID: ' + str(room.id))
	return

def command_teleport(arguments):
	sender = arguments['Sender']
	args = arguments['Arguments']
	world = arguments['World']
	room = sender.location

	if (len(args) < 1):
		sender.send('Usage: teleport <Room ID|User Name>')
		return

	input = args[0]
	target_room = world.find_room(id=input)
	if (target_room is not None):
		for player in room.players:
			if (player != sender):
				player.send(sender.display_name + ' fades into a mist and vanishes ...')
		sender.send('The world around you slowly fades away ...')
		sender.set_location(target_room)
		for player in target_room.players:
			if (player != sender):
				player.send('A myst appears and forms into ' + sender.display_name + '.')

		command_args = {
			'Sender': sender,
			'World': world
		}
		command_look(command_args)
		return

	sender.send('Unknown room.')
	return

def command_move(arguments):
	sender = arguments['Sender']
	world = arguments['World']
	input = arguments['Input']

	if (input == ''):
		sender.send('Usage: move <name of exit>')
		return

	for exit in sender.location.exits:
		if (string.lower(exit.name) == string.lower(input)):
			sender.send('You move out.')
			sender.set_location(exit.target_id)
			command_args = {
				'Sender': sender,
				'World': world
			}
			command_look(command_args)
			return

	sender.send('I do not see that.')
	return

def command_edit(arguments):
	sender = arguments['Sender']
	world = arguments['World']
	input = arguments['Input']

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

def command_inventory(arguments):
	sender = arguments['Sender']

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

def command_take(arguments):
	sender = arguments['Sender']
	input = arguments['Input']

	if (input == ''):
		sender.send('Usage: take <object name>')
		return

	for item in sender.location.items:
		if (item.name == input):
			sender.send('Taken.')
			return

	sender.send('I do not see that.')

def command_passwd(arguments):
	sender = arguments['Sender']
	input = arguments['Input']

	if (input == ''):
		sender.send('Usage: passwd <password>')
		return

	sender.set_password(input)
	sender.send('Your password has been changed. Remember it well.')

def command_craft(arguments):
	sender = arguments['Sender']
	input = arguments['Input']

	if (input == ''):
		sender.send('Usage: craft <new item name>')
		return

	world = arguments['World']

	item = world.create_item(input, '<Unset>', sender, sender.inventory)
	sender.send('Item crafted.')


# Callbacks
def callback_client_authenticated(arguments):
	client = arguments['Sender']
	client.is_editing = False
	client.edit_target = None

	world = arguments['World']

	command_args = {
		'Sender': client,
		'World': world
	}
	command_look(command_args)
	return

def callback_message_sent(arguments):
	sender = arguments['Sender']
	if (sender.is_editing):
		edit.receive_input(arguments)
		return True

	input = arguments['Input']
	world = arguments['World']

	# TODO: Make this not suck
	if (input[0:2] == ': '):
		command_args = {
			'Sender': sender,
			'World': world,
			'Input': input[2:]
		}
		command_pose(command_args)
		return True
	elif (input[0] == ':'):		
		command_args = {
			'Sender': sender,
			'World': world,
			'Input': input[1:]
		}
		command_pose(command_args)
		return True

	if (input[0:2] == '" '):
		command_args = {
			'Sender': sender,
			'World': world,
			'Input': input[2:]
		}
		command_say(command_args)
		return True
	elif (input[0] == '"'):
		command_args = {
			'Sender': sender,
			'World': world,
			'Input': input[1:]
		}
		command_say(command_args)
		return True

	return False

# Function calls
def initialize(config):
	print(config.get_index('Test', str))
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
		}
	}
	return command_dict

def get_callbacks():
	callback_dict = {
		'onClientAuthenticated': callback_client_authenticated,
		'onMessageSent': callback_message_sent
	}
	return callback_dict
