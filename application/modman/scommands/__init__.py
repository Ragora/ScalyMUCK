"""
      ScalyMUCK Normal Commands
      This mod code is simply ScalyMUCK's
      default user commands.
"""

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
	world_instance = arguments['World']
	sender = arguments['Sender']
	input = arguments['Input']
	room = sender.location

	for player in room.players:
		if (player != sender):
			player.send(sender.name + ' says, "' + input + '"')

	sender.send('You say, "' + input + '"')
	return

def command_pose(arguments):
	return

def command_look(arguments):
	sender = arguments['Sender']
	room = sender.location
	
	sender.send(room.name)
	sender.send('Obvious Exits: ')
	sender.send('	None')
	sender.send('People: ')
	for player in room.players:
		sender.send('	' + player.display_name)
	sender.send('Items: ')
	#for item in room.items:
	#	sender.send(item.name)
	sender.send('	None')
	sender.send('Description:')
	sender.send(room.description)

	return

def callback_client_authenticated(arguments):
	client = arguments['Client']
	world = arguments['World']

	command_args = {
		'Sender': client,
		'World': world
	}
	command_look(command_args)
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
		}
	}
	return command_dict

def get_callbacks():
	callback_dict = {
		'onClientAuthenticated': callback_client_authenticated
	}
	return callback_dict
