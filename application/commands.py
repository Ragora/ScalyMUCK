"""
	commands.py
	Commands for ScalyMUCK
	Copyright (c) 2012 Liukcairo
"""

import string 

# There are no used library imports

import models
import muckserver
import database
import hash

# Normal User Level Commands
def cmd_look(sending_user, input_string, input_arguments, db_session):	
	input_string = string.lower(input_string)
	target_item = db_session.query(models.Item).filter_by(name=input_string,location_id=sending_user.location_id).first()
	if (target_item is not None):
		sending_user.connection.send(target_item.display_name + ' --\n')
		sending_user.connection.send(target_item.description + '\n')
		return
	target_user = db_session.query(models.User).filter_by(name=input_string,location_id=sending_user.location_id).first()
	if (target_user is not None):
		target_connection = muckserver.find_connection(target_user.id)
		if (target_connection is not None):
			target_connection.send('+++++++ ' + sending_user.display_name + ' just looked at you!\n')
		sending_user.connection.send('He sees you looking at him.\n')
		sending_user.connection.send(target_user.display_name + ' --\n')
		sending_user.connection.send(target_user.description + '\n')
		sending_user.connection.send('Inventory ---\n')
		has_items = False
		for item in target_user.inventory:
			sending_user.connection.send(item.display_name + '\n')
			has_items = True
		if (has_items is False):
			sending_user.connection.send('Nothing.\n')
		return
		
	if (len(input_arguments) > 0):
		sending_user.connection.send('I do not see that.\n')
		return

	target_room = db_session.query(models.Room).filter_by(id=sending_user.location_id).first()
	sending_user.connection.send('-- ' + target_room.display_name + ' --\n')
	sending_user.connection.send(target_room.description + '\n')
	sending_user.connection.send('Obvious Exits-- \n')
	
	target_exits = target_room.exits
	
	has_exits = False
	for target_exit in target_exits:
		has_exits = True
		sending_user.connection.send(target_exit.display_name + '\n')
	if (has_exits == False):
		sending_user.connection.send('There are none.\n')
		
	sending_user.connection.send('Contents-- \n')
	
	target_users = db_session.query(models.User).filter_by(location_id=sending_user.location_id)
	for target_user in target_users:
		sending_user.connection.send(target_user.display_name + '\n')
		
	target_items = db_session.query(models.Item).filter_by(location_id=sending_user.location_id)
	for target_item in target_items:
		sending_user.connection.send(target_item.display_name + '\n')
	return
	
def cmd_ping(sending_user, input_string, input_arguments, db_session):
	sending_user.connection.send('Pong.\n')
	return
	
def cmd_say(sending_user, input_string, input_arguments, db_session):
	target_room = db_session.query(models.Room).get(sending_user.location_id)
	target_room.broadcast(sending_user.display_name + ' says, "' + input_string + '"\n',sending_user)
	sending_user.connection.send('You say, "' + input_string + '"\n')
	return
	
def cmd_spoof(sending_user, input_string, input_arguments, db_session):
	target_room = db_session.query(models.Room).get(sending_user.location_id)
	if (len(input_arguments) == 0):
		sending_user.connection.send('There is nothing to say.\n')
		return
		
	target_user = db_session.query(models.User).filter_by(name=string.lower(input_arguments[0])).first()
	if (target_user is None):
		target_room.broadcast(input_string + '\n')
	else:
		target_room.broadcast('*** ' + input_string + '\n')
	return

def cmd_wwi(sending_user, input_string, input_arguments, db_session):
	connections = muckserver.connection._connections
	sending_user.connection.send('---WWI start.\n')
	sending_user.connection.send('Name		S	Species		Location Name\n')
	
	for connection in connections:
		if (connection.id == 0): continue
		user_data = db_session.query(models.User).get(connection.id)
		location_data = db_session.query(models.Room).get(user_data.location_id)
		sending_user.connection.send(user_data.display_name + '	N	<Unset>		' + location_data.display_name + '\n')
	sending_user.connection.send('---WWI end.\n')
	return	
	
def cmd_pose(sending_user, input_string, input_arguments, db_session):
	target_room = db_session.query(models.Room).get(sending_user.location_id)
	target_room.broadcast(sending_user.display_name + ' ' + input_string + '\n')
	return
	
def cmd_inventory(sending_user, input_string, input_arguments, db_session):
	sending_user.connection.send('You have:\n')
	has_items = False
	for item in sending_user.inventory:
		sending_user.connection.send(item.display_name + '\n')
		has_items = True
	if (has_items == False):
		sending_user.connection.send('Nothing.\n')
	return
	
def cmd_take(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sending_user.connection.send('Take what?\n')
		return
		
	target_item = db_session.query(models.Item).filter_by(location_id=sending_user.location_id,
													      name=string.lower(input_string)).first()

	if (target_item is None):
		sending_user.connection.send("I don't see that.\n")
	else:
		sending_user.connection.send('Taken.\n')
		target_item.location = 0
		sending_user.inventory.append(target_item)
		current_room = db_session.query(models.Room).get(target_item.location_id)
		current_room.items.remove(target_item)
		db_session.add(target_item)
		db_session.add(current_room)
		db_session.commit()
		current_room.broadcast(sending_user.display_name + ' takes ' + target_item.display_name + '.\n', sending_user)
	return
	
def cmd_drop(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sending_user.connection.send('Drop what?\n')
		return
		
	target_item = None
	for item in sending_user.inventory:
		if (item.name == string.lower(input_string)):
			target_item = item
			break
	if (target_item is None):
		sending_user.connection.send("I don't see that.\n")
		return
	target_room = db_session.query(models.Room).get(sending_user.location_id)
	sending_user.inventory.remove(target_item)
	target_room.items.append(target_item)
	target_item.location_id = target_room.id
	db_session.add(target_room)
	db_session.add(sending_user)
	db_session.add(target_item)
	db_session.commit()
	target_room.broadcast(sending_user.display_name + ' drops ' + target_item.display_name + '.\n', sending_user)
	sending_user.connection.send("Dropped.\n")
	return
	
def cmd_move(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sender.send('Move where?\n')
		return
		
	target_exit = db_session.query(models.Exit).filter_by(parent=sending_user.location_id,
													   code=string.lower(input_arguments[0])).first()
													   
	if (target_exit is None):
		sender.send('No such exit.\n',0)
		return
		
	target_room = db_session.query(models.Room).get(target_exit.link)
	current_room = db_session.query(models.Room).get(sending_user.location_id)
	
	current_room.users.remove(sending_user)
	target_room.users.append(sending_user)
	sending_user.location = target_room.id
	
	current_room.broadcast(sending_user.display_name + ' leaves the room.\n',sending_user)
	sending_user.connection.send('You leave the room.\n')
	target_room.broadcast(sending_user.display_name + ' enters the room.\n',sending_user)
	
	db_session.add(current_room)
	db_session.add(target_room)
	db_session.add(sending_user)
	db_session.commit()
	cmd_look(sending_user, '', [], database.new_session())
	return
	
def cmd_page(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) <= 1):
		sending_user.connection.send('You did not specify a user/message. Usage:\npage <user> <message...>\n')
		return
	user_name = string.lower(input_arguments[0])
	user_name_disp = input_arguments[0]
	user_data = db_session.query(models.User).filter_by(name=user_name).first()
	if (user_data is None):
		sending_user.connection.send('User "' + user_name_disp + '" does not exist.\n')
		return
	
	input_string = ''
	is_first = True
	for input_word in input_arguments:
		if (is_first):
			input_string = input_string + input_word
		else:
			input_string = input_string + ' ' + input_word
		is_first = False
	user_connection = muckserver.find_connection(user_data.id)
	if (user_connection is not None):
		input_string = string.replace(input_string, user_name_disp + ' ','',1)
		user_connection.send(sending_user.display_name + ' from afar, says, "' + input_string + '"\n')
		sending_user.connection.send('From afar, you say to ' + user_data.display_name + ', "' + input_string + '"\n')
	else:
		sending_user.connection.send('User "' + user_name_disp + '" is not online right now.\n')
	return
		
def cmd_teleport(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sending_user.connection.send('You did not specify a room.\n')
		return False
	
	input_string_disp = input_string
	input_string = string.lower(input_string)
	target_room = db_session.query(models.Room).get(input_string)
	current_room = db_session.query(models.Room).get(sending_user.location_id)
	
	if (target_room is None):
		target_room = db_session.query(models.Room).filter_by(name=input_string).first()
	if (target_room is None):
		sending_user.connection.send('No such room "' + input_string_disp + '"\n')
		return False
			
	current_room.users.remove(sending_user)
	target_room.users.append(sending_user)
	sending_user.location_id = target_room.id
	db_session.add(current_room)
	db_session.add(target_room)
	db_session.add(sending_user)
	db_session.commit()
	sending_user.connection.send('You fade away into nothing...\n')
	current_room.broadcast(sending_user.display_name + ' fades away into nothing...\n', sending_user)
	target_room.broadcast('A mist appears and forms into ' + sending_user.display_name + '.\n')
	cmd_look(sending_user, '', [], database.new_session())
	return True
	
def cmd_craft(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sending_user.connection.send('You did not specify a name.\n')
		return False
		
	target_object = db_session.query(models.Item).filter_by(name=string.lower(input_string)).first()
	if (target_object is not None):
		sending_user.connection.send('That object already exists.\n')
		return
	target_object = models.Item(input_string, '<Unset>', sending_user.id, sending_user.location_id)
	target_object.location_id = 0
	target_object.owner_id = sending_user.id
	sending_user.inventory.append(target_object)
	db_session.add(target_object)
	db_session.add(sending_user)
	db_session.commit()
	sending_user.connection.send('You craft a "' + input_string + '".\n')
	return
	
def cmd_dig(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sending_user.connection.send('You did not specify a name.\n')
		return False
		
	target_room = db_session.query(models.Room).filter_by(name=string.lower(input_string)).first()
	if (target_room is not None):
		sending_user.connection.send('That room already exists.\n')
		return
	target_room = models.Room(input_string, '<Unset>', sending_user.id, [], [], [])
	db_session.add(target_room)
	db_session.commit()
	target_room = db_session.query(models.Room).filter_by(name=string.lower(input_string)).first()
	sending_user.connection.send('You new room is available at ID ' + str(target_room.id) + '.\n')
	return
	
def cmd_newpass(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sending_user.connection.send('You did not specify a new password.\n')
		return False
	sending_user.hash = hash.generate_hash(input_string)
	db_session.add(sending_user)
	db_session.commit()
	sending_user.connection.send('Password changed.\n')
	return
	
def cmd_link(sending_user, input_string, input_arguments, db_session):
	return
	
def cmd_recycle(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 1):
		sending_user.connection.send('You did not specify an object.\n')
		return False
	target_item = None
	input_string = string.lower(input_string)
	for item in sending_user.inventory:
		if(item.id == input_string):
			target_item = item
			break
		if (item.name == input_string):
			target_item = item
			break
	if (target_item is None):
		sending_user.connection.send('I do not see that.\n')
		return
	if (target_item.owner_id != sending_user.id):
		target_user = db_session.query(models.User).get(target_item.owner_id)
		sending_user.connection.send('This object is not yours. It belongs to: ' + target_user.display_name + '.\n')
		return
	sending_user.inventory.remove(target_item)
	db_session.delete(target_item)
	db_session.add(sending_user)
	db_session.commit()
	sending_user.connection.send('Recycled.\n')
	return
	
def cmd_chown(sending_user, input_string, input_arguments, db_session):
	if (len(input_arguments) < 2):
		sending_user.connection.send('You did not specify a new owner/object.Usage:\nchown <target> <item name>\n')
		return False
	target_item = None
	for item in sending_user.inventory:
		if(item.id == input_string):
			target_item = item
			break
		elif (item.name == input_string):
			target_item = item
			break
	if (target_item is None):
		sending_user.connection.send('I do not see that.\n')
		return
	if (target_item.owner_id != sending_user.id):
		target_user = db_session.query(models.User).get(target_item.owner_id)
		sending_user.connection.send('This object is not yours. It belongs to: ' + target_user.display_name + '.\n')
		return
	user_name_resp = input_arguments[0]
	user_name = string.lower(input_arguments[0])
	target_user = db_session.query(models.User).filter_by(name=user_name)
	if (target_user is None):
		sending_user.connection.send('No such user, "' + user_name_resp + '".\n')
		return
	target_item_name = input_arguments.pop(0)
	target_name = ''
	first_word = True
	for word in target_item_name:
		if (first_word):
			target_name = target_name + word
		else:
			target_name = target_name + ' ' + word
		first_word = False
	target_name_resp = string.lower(target_name)
	target_item = None
	for item in sending_user.inventory:
		if (item.name == target_name):
			target_item = item
			break
	if (target_item is None):
		sending_user.connection.send('I don\'t see that.')
		return
		
	target_item.owner_id = target_user.id
	db_session.add(target_item)
	db_session.commit()
	sending_user.connection.send('Item is now owned by ' + target_user.display_name + '.\n')
	return
	
def cmd_examine(sending_user, input_string, input_arguments, db_session):	
	input_string = string.lower(input_string)
	target_item = db_session.query(models.Item).filter_by(name=input_string,location_id=sending_user.location_id).first()
	if (target_item is not None):
		target_item_owner = db_session.query(models.User).get(target_item.owner_id)
		sending_user.connection.send(target_item.display_name + '\'s Details\n')
		sending_user.connection.send('-----------------------')	
		sending_user.connection.send('ID: ' + str(target_item.id) + '\n')
		sending_user.connection.send('Location ID: ' + str(target_item.location_id) + '\n')
		if (target_item_owner is not None):
			sending_user.connection.send('Owner: ' + target_item_owner.display_name + ' (' + target_item_owner.id + ')\n')
		else:
			sending_user.connection.send('Owner: Nobody.\n')
		return
	target_user = db_session.query(models.User).filter_by(name=input_string,location_id=sending_user.location_id).first()
	if (target_user is not None):
		target_connection = muckserver.find_connection(target_user.id)
		sending_user.connection.send(target_user.display_name + '\'s Details\n')
		sending_user.connection.send('-----------------------\n')	
		sending_user.connection.send('ID: ' + str(target_user.id) + '\n')
		sending_user.connection.send('Location ID: ' + str(target_user.location_id) + '\n')
		sending_user.connection.send('Is Admin: ' + str(target_user.is_admin) + '\n')
		sending_user.connection.send('Is Super Admin: ' + str(target_user.is_sadmin) + '\n')
		sending_user.connection.send('Is Owner: ' + str(target_user.is_owner) + '\n')
		return
		
	if (len(input_arguments) > 0):
		sending_user.connection.send('I do not see that.\n')
		return

	target_room = db_session.query(models.Room).filter_by(id=sending_user.location_id).first()
	target_room_owner = db_session.query(models.User).get(target_room.owner_id)
	sending_user.connection.send('-- ' + target_room.display_name + '\'s Details\n')		
	sending_user.connection.send('ID: ' + str(target_room.id) + '\n')
	if (target_room_owner is not None):
		sending_user.connection.send('Owner: ' + target_room_owner.display_name + ' (' + target_room_owner.id + ')\n')
	else:
		sending_user.connection.send('Owner: Nobody.\n')
	return
	
# Owner Level Commands
def cmd_add_user(sending_user, input_string, input_arguments, db_session):
	if (sending_user.is_owner == 0):
		sender.connection.send('You are not magical enough.\n')
		return
	if (len(input_arguments) != 2):
		sending_user.connection.send('You did not specify a username/password. Usage:\naddUser <Name> <Password>\n')
		return

	user_name_disp = input_arguments[0]
	user_name = string.lower(user_name_disp)
	target_user = db_session.query(models.User).filter_by(name=user_name).first()
	
	if(target_user is not None):
		sending_user.connection.send('User ' + user_name_disp + ' already exists. Pick a new name.\n')
		return
	else:
		new_user = models.User(user_name_disp,'<Unset>',input_arguments[1], 1, [], 0, 0, 0)
		db_session.add(new_user)
		db_session.commit()
		sending_user.connection.send('User ' + user_name_disp + ' added.\n',0)
	return	
	
# Our actual Command Listings
entries = { 
				# Normal Level Cmds
				'look': cmd_look, 
				'examine': cmd_examine,
				'ping': cmd_ping,
				'say': cmd_say,
				'pose': cmd_pose,
				'wwi': cmd_wwi,
				'page': cmd_page, 'p': cmd_page, 'pm': cmd_page,
				'whisper': cmd_page, 'w': cmd_page,
				'teleport': cmd_teleport, 't': cmd_teleport,
				'inventory': cmd_inventory, 'inv': cmd_inventory,
				'take': cmd_take,
				'drop': cmd_drop,
				'move': cmd_move,
				'craft': cmd_craft,
				'dig': cmd_dig,
				'spoof': cmd_spoof,
				'newpassword': cmd_newpass,
				'link': cmd_link,
				'recycle': cmd_recycle,
				'chown': cmd_chown,
				# Admin Level Cmds
				# SAdmin Level Cmds
				# Owner Level Cmds
				'adduser': cmd_add_user
			}	
