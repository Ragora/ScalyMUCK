"""
	muck_server.py
	Copyright (c) 2012 Liukcairo
	A MUCK server built off of telnet_host.py
"""
import string
import sys

# There are no external library imports

import telnethost 
import models
import hash
import commands
import database

class MUCKServer(telnethost.TelnetHost):

	def onClientConnected(self, host):
		host.id = 0
		try:
			with open("data/welcomeMessage.txt") as f:
				for line in f:
					if (string.find(line, '\n') == -1):
						line = line + '\n'
					host.send(line, 0)
				f.close()
			del f
		except:
			host.send('-- Unable to locate welcome message file!\n', 0)
		return
		
	def onClientDisconnect(self, host):
		if (host.id != 0):
			session = database.new_session()
			target_user = session.query(models.User).get(host.id)
			target_room = session.query(models.Room).get(target_user.location_id)
			target_room.broadcast(target_user.display_name + ' disconnected.\n',target_user)
		del host
		
	def onReceiveData(self, data, host):
		return
		
	def onReceiveLine(self, line, host):
		line = string.replace(line,"\r","")
		line = string.replace(line,"\n","")
		line_data = string.split(line, ' ')
		word_count = len(line_data)
		if (host.id == 0):
			if (string.lower(line_data[0]) != 'connect'):
				host.send('It appears you are not logged in.\nYou may login with:\nconnect <user> <password>\n',0)
				return
			elif (word_count < 3):
				host.send('You forgot your username/password entries.\n',0)
				return
			else:
				user_name = line_data[1]
				password = line_data[2]
				
				session = database.new_session()
				user_data = session.query(models.User).filter_by(display_name=user_name).first()
				
				if (user_data is None):
					host.send('Invalid username/password combination.\n',0)
					return
				elif (hash.check_password(password, user_data.hash)):
					current_connection = find_connection(user_data.id)
					target_room = session.query(models.Room).get(user_data.location_id)
					if (current_connection is not None):
						current_connection.send('Your connection has been replaced.\n')
						current_connection.disconnect()
						current_connection.shutdown()
						target_room.broadcast(user_data.display_name + ' kicked off an old connection.\n',user_data)
				
				
					target_room.broadcast(user_data.display_name + ' connected.\n',user_data)
					host.id = user_data.id
					host.send('\n\n\n')
					user_data.connection = host
					commands.cmd_look(user_data, '', [], session)
					return
				else:
					host.send('Invalid username/password combination.\n',0)
					return
		else:
			if (line[0] == ':'):			
				session = database.new_session()
				user_data = session.query(models.User).filter_by(id=host.id).first()
				user_data.connection = host
				line = string.replace(line,':','',1)
				line = string.lstrip(line)
				line_data = string.split(line, ' ')
				line_data.pop(0)
				input_arguments = line_data
				commands.cmd_pose(user_data, line, input_arguments, session)
				return
			elif (line[0] == '"'):			
				session = database.new_session()
				user_data = session.query(models.User).filter_by(id=host.id).first()
				user_data.connection = host
				line = string.replace(line,'"','',1)
				line = string.lstrip(line)
				line_data = string.split(line, ' ')
				line_data.pop(0)
				input_arguments = line_data
				commands.cmd_say(user_data, line, input_arguments, session)
				return
				
			command = string.lower(line_data[0])
			command_keys = commands.entries.keys()
			if (command_keys.count(command) != 0):
				function_call = commands.entries[command]
				
				line_data.pop(0)
				input_arguments = line_data
					
				is_first = True
				input_string = ''
				for word in line_data:
					if (is_first == False):
						input_string = input_string + ' ' + word
					else:
						input_string = input_string + word
					is_first = False
				
				session = database.new_session()
				user_data = session.query(models.User).filter_by(id=host.id).first()
				user_data.connection = host
			
				function_call(user_data, input_string, input_arguments, session)
			else:
				host.send('I do not know.\n',0)
		return
				
	def debugMessage(self, msg):
		print('Debug Message: ' + msg)
		

global connection
connection = MUCKServer()

def find_connection(id):
	global connection
	for connection_obj in connection._connections:
		if (connection_obj.id == id):
			return connection_obj
	return None 
