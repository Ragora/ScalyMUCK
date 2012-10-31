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

def command_say(database_engine, sender, args):
	print(database_engine)
	return

def command_pose(database_engine, sender, args):
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
		'pose': command_pose
	}
	
	command_help = {
		'say': 'Makes you say something. Only visible to the current room you\'re in.',
		'pose': 'Used to show arbitrary action. Only visible to the current room you\'re in.'
	}
	return [command_dict, command_help]