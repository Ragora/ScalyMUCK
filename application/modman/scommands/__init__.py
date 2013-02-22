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
def command_say(data):
	world_instance = data['World']
	sender = data['Sender']
	args = data['Arguments']

	return

def command_pose(data):
	return

def command_look(data):
	return

"""
      get_commands
      
      This function is used by modloader to retrieve any
      custom commands that the mod may want to implement.
      Return None if there are no commands to implement.
"""
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
			'Desription': 'Used to show arbitrary action. Only visible to the current room you\'re in.'
		},

		'look': 
		{
			'Command': command_look,
			'Description': 'Get your bearings. Look around in the local area to see what you can see.'
		}
	}
	return command_dict

"""
	get_callbacks

	This function is used by the modloader to retrieve
	any custom callbacks that the mod may want to have access to.
	Return none if there are no commands to implement.
"""
def get_callbacks():
	return None
