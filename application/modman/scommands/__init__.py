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
author = 'Liukcairo'

def command_say(world_instance, sender, args):
	print(database_engine)
	return

def command_pose(world_instance, sender, args):
	return

def command_look(world_instance, sender, args):
	return

"""
      get_commands
      
      This function is used by modloader to retrieve any
      custom commands that the mod may want to implement.
      Return None if there are no commands to implement.
"""
def get_commands():
	command_dict = {
		'say': command_say,
		'pose': command_pose,
		'look': command_look
	}
	
	command_help = {
		'say': 'Makes you say something. Only visible to the current room you\'re in.',
		'pose': 'Used to show arbitrary action. Only visible to the current room you\'re in.',
		'look': 'Get your bearings. Look around in the local area to see what you can see.'
	}
	return [command_dict, command_help]