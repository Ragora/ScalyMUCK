"""
    __init__.py
    
    ScalyMUCK's Mod manager code, it's used
    to import functionality from all sorts
    of installed modifications.
"""

import os
import string

# This class is pretty useless as of now but it's intended for easy access to mod-specific AI's and items, etc
class Mod():
	name = None
	description = None
	author = None
	commands = None
	command_help = None
	
	version_major = None
	version_minor = None
	version_revision = None
	
	server_version_major = None
	server_version_minor = None
	server_version_revision = None

def get_mod_list():
	files = os.listdir('modman/')
	
	mod_list = [ ]
	for file in files:
		if (string.find(file, '.') == -1):
			try:
				with open('modman/' + file + '/__init__.py') as f:
					pass
			except IOError as e:
					continue
			mod_list.append(file)
	return mod_list

def load_mod(name):
	if (name in get_mod_list()):
		imported =  __import__('modman.' + name, globals(), locals(), [''], -1)
		command_listing = imported.get_commands()
		
		mod_data = Mod()
		mod_data.name = imported.name
		mod_data.description = imported.description
		mod_data.author = imported.author
		mod_data.version_major = imported.version_major
		mod_data.version_minor = imported.version_minor
		mod_data.version_revision = imported.version_revision
		mod_data.server_version_major = imported.server_version_major
		mod_data.server_version_minor = imported.server_version_minor
		mod_data.server_version_revision = imported.server_version_revision
		
		mod_data.commands = command_listing[0]
		mod_data.command_help = command_listing[1]
		
		return mod_data
	else:
		return None