"""
	ScalyMUCK edit command "runtime"

	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

import game.models as models

def display_menu(arguments):
	menu = arguments['Menu']
	sender = arguments['Sender']

	target = sender.edit_target
	if (menu == 'Main'):
		sender.send(' ')
		sender.send('ScalyMUCK Edit v0.0.0')
		sender.send('Copyright (c) 2013 Robert MacGregor')
		sender.send(' ')
	elif (menu == 'EditMain'):
		if (type(target) is models.Player):
			sender.send('Player Name: ' + target.display_name)
		else:
			sender.send('Object Name: ' + target.name)

		sender.send('Object Type: ' + str(type(target)))
	return

def receive_input(arguments):
	sender = arguments['Sender']
	world = arguments['World']
	input = arguments['Input']

	data = string.split(input, ' ')
	command = data[0]

	sender.send('Editor: Unknown command')
	return
