"""
      ScalyMUCK example plugin.
"""

server_version_major = 1
server_version_minor = 0
server_version_revision = 0

version_major = 1
version_minor = 0
version_revision = 0
name = 'ScalyMUCK Example Mod'
description = 'Example Mod implementation.'
copyright = 'Copyright (c) 2013 <You>'
author = '<You>'

# Commands
def command_example(data):
	return

# Callbacks
def callback_message_received(data):
	return

"""
      get_commands
      
      This function is used by modloader to retrieve any
      custom commands that the mod may want to implement.
      Return None if there are no commands to implement.
"""
def get_commands():
	command_dict = {
		'example': 
		{ 
			'Command': command_example,
			'Description': 'Example implementation.'
		},
	}
	return command_dict

"""
	get_callbacks

	This function is used by the modloader to retrieve
	any custom callbacks that the mod may want to have access to.
	Return none if there are no commands to implement.
"""
def get_callbacks():
	callback_dict = {
		'onMessageReceived': 
		{
			'Command': callback_message_received
		}
	}
	return callback_dict
