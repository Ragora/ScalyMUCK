"""
	server.py

	This is the main ScalyMUCK server code,
	it performs the initialisation of various
	systems and is the binding of everything.
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import sys
import string
from time import gmtime, strftime

from sqlalchemy import create_engine
from miniboa import TelnetServer
import bcrypt

import models
import daemon
import interface
from world import World
from log import Log

class Server(daemon.Daemon):
	is_running = False
	is_daemon = False
	config = None
	telnet_server = None
	
	work_factor = None
	
	world_instance = None
	logger = None

	welcome_message_data = ''
	exit_message_data = ''
	
	pending_connection_list = [ ]
	established_connection_list = [ ]

	interface = None
	
	version_major = 1
	version_minor = 0
	version_revision = 0
	
	def __init__(self, pid, config, data_path):
		self.pidfile = pid
		
		self.data_path = data_path
		self.logger = Log(data_path + 'log.txt', pid is None)

		server_config_location = 'config/settings_server.cfg'
		gameplay_config_location = 'config/settings_gameplay.cfg'
  
		self.config = config
		
		try:
			with open('config/welcome_message.txt') as f:
				for line in f:
					if (string.find(line, '\n') == -1):
						line = line + '\n'
					self.welcome_message_data += line
				f.close()
				self.welcome_message_data += '\n'
		except IOError as e:
			self.welcome_message_data = 'Unable to load welcome message!'
			
		try:
			with open('config/exit_message.txt') as f:
				for line in f:
					if (string.find(line, '\n') == -1):
						line = line + '\n'
					self.exit_message_data += line
				f.close()
				self.exit_message_data += '\n'
		except IOError as e:
			self.exit_message_data = 'Unable to load exit message!'
	
	"""
		server.initialise_server

		This function is called by both no_daemon.py and manage_daemon.py
		to start the actual MUCK server code.
	"""
	def initialise_server(self):
		server_version_string = '%s.%s.%s' % (self.version_major, self.version_minor, self.version_revision)
		self.logger.write('Server Version: ' + server_version_string)

		database_exists = True
		database_location = self.data_path + 'Database.db'
		try:
			with open(database_location) as f: pass
		except IOError as e:
			self.logger.write('This appears to be your first time running the ScalyMUCK server. We must initialise your database ...')
			database_exists = False

		database_engine = create_engine('sqlite:///' + database_location, echo=False)
		models.Base.metadata.create_all(database_engine)
		self.world_instance = World(database_engine)
		
		if (database_exists is False):
			self.initialise_database()
		
		self.telnet_server = TelnetServer(port=self.config.get_index('ServerPort', int),
						address=self.config.get_index('ServerAddress', str),
					        on_connect = self.on_client_connect,
					        on_disconnect = self.on_client_disconnect,
					        timeout = 0.05)
		self.is_running = True
		
		print(self.config.get_index('Debug', bool))
		self.interface = interface.Interface(self.logger, self.config.get_index('Debug', bool))
		self.logger.write('\nScalyMUCK successfully initialised.')
	
	"""
	      server.initialise_database
	      
	      This function is called internally; it's just here to separate logic a bit.
	"""
	def initialise_database(self):
		portal_room = self.world_instance.create_room('Portal Room Main')
		raptor_jesus = self.world_instance.create_player('RaptorJesus', 'ChangeThisPasswordNowPlox', self.work_factor, portal_room)
		self.logger.write('Database successfully initialised.')
		return
	
	"""
	      server.is_active
	      
	      This function returns the active state of the
	      server. It's only used in no_daemon.py to obtain
	      a while loop that terminates when the server
	      must stop for any reason.
	"""
	def is_active(self):
		return self.is_running

	def is_running(self):
		return self.is_running

	"""
	      server.update
	      
	      This function is used to update the server status
	      every CPU pass. This handles client input when 
	      they are not logged in for security purposes.
	"""
	def update(self):
		self.telnet_server.poll()
		
		for connection in self.pending_connection_list:
			if (connection.cmd_ready is True):
				data = connection.get_command()
				# There's a fixed connect command here for security reasons
				command_data = string.split(data, ' ')
				if (len(command_data) < 3):
					connection.send('You did not specify all of the required arguments.\n')
				elif (len(command_data) >= 3 and command_data[0].lower() == 'connect'):
					name = command_data[1].lower()
					password = command_data[2]
					
					target_player = self.world_instance.find_player(name=name)
					if (target_player is None):
						connection.send('You have specified an invalid username/password combination.\n')
					else:
						player_hash = target_player.hash
						if (player_hash == bcrypt.hashpw(password, player_hash) == player_hash):
							connection.id = target_player.id
							connection.player = target_player
							target_player.connection = connection

							#callback_data = {
							#	'Client': connection.player,
							#	'Room': None,
							#	'World': self.world_instance
							#}
							#for callback in self.callback_entries['onClientAuthenticated']:
							#	callback(callback_data)

							for player in self.established_connection_list:
								if (player.id == connection.id):
									# Fixme: This message isn't dispatched as telnet_server.poll is not called before the player is deactivated
									player.send('Your connection has been replaced.\n')
									player.deactivate()
									self.established_connection_list.remove(player)
									break
							self.pending_connection_list.remove(connection)	
							self.established_connection_list.append(connection)
						else:
							connection.send('You have specified an invalid username/password combination.\n')
				elif (len(command_data) >= 3 and command_data[0].lower() != 'connect'):
					connection.send('You must use the "connect" command:\n')
					connection.send('connect <username> <password>\n')

		# With already connected clients, we'll now deploy the command interface.
		for connection in self.established_connection_list:
			input = connection.get_command()

			if (input is not None):
				#callback_data = {
				#	'Sender': connection.player,
				#	'Room': None, # TODO: Correct this
				#	'World': self.world_instance,
				#	'Input': input
				#}
				#intercept_input = False
				#for callback in self.callback_entries['onMessageSent']:
				#	if (callback(callback_data)): # TODO: Fix this from error'ing up on a bad callback
				#		intercept_input = True
				self.interface.parse_command(connection.player, input)
					

	def run(self):
	    self.initialise_server()
	    while (self.is_running()):
		self.update()

	"""
	      server.on_client_connect
	      
	      This is a function that is called by miniboa in the event
	      a remote client connects to the server.
	"""
	def on_client_connect(self, client):
		self.logger.write('Received client connection from ' + client.address + ':' + str(client.port))
		client.send(self.welcome_message_data)
		self.pending_connection_list.append(client)
	 
	"""
	      server.on_client_disconnect
	      
	      This is a function that is called by miniboa in the event
	      a remote client disconnects from the server.
	"""
	def on_client_disconnect(self, client):
		self.logger.write('Received client disconnection from ' + client.address + ':' + str(client.port))
		if (client in self.pending_connection_list):
			self.pending_connection_list.remove(client)
		elif (client in self.established_connection_list):
			self.established_connection_list.remove(client)
