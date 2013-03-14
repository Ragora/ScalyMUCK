"""
	ScalyMUCK edit command "runtime"

	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

import game.models as models

_edit_options = [ (0, 'Exit the Editor'), (1, 'Change Name') ]
def display_menu(client, menu):
	menu = arguments['Menu']
	sender = arguments['Sender']
	sender.edit_menu = menu

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
		sender.send('Options----')
		sender.send('0.) Exit the Editor')
		sender.send('1.) Change Name')
		sender.send('2.) Change Description')
	return

def receive_input(sender, input):

	data = string.split(input, ' ')
	command = data[0]

	if (sender.edit_menu == 'EditMain'):
		if (input == ''):
			arguments['Menu'] = 'EditMain'
			display_menu(arguments)
		elif (input == '0'):
			sender.send('Editor: Left the editor.')
			sender.is_editing = False
		elif (input == '1'):
			sender.edit_menu = 'EditName'
			sender.send('Editor: Next thing you type will become the new name. If you wish to cancel, simply leave the input blank and hit enter.')
		else:
			sender.send('Editor: Unknown command')
	elif (sender.edit_menu == 'EditName'):
		if (input == ''):
			arguments['Menu'] = 'EditMain'
			sender.send('You canceled the name edit.')
			display_menu(arguments)
		else:
			print(sender.edit_target)
			sender.edit_target.set_name(input)
			sender.send('Object renamed.')
			arguments['Menu'] = 'EditMain'
			display_menu(arguments)
			
	return
