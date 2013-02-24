"""
	server.py
	This is the main ScalyMUCK server code,
	it performs the initialisation of various
	systems and is the binding of everything.
	Copyright (c) 2012 Liukcairo
"""

import sys
import string

from sqlalchemy import create_engine
from miniboa import TelnetServer
import bcrypt

import settings
import models
import daemon
import modman
import world
import log

class Server(daemon.Daemon):
	is_running = False
	is_daemon = False
	server_settings = None
	telnet_server = None
	database_engine = None
	
	home_directory = None
	database_location = None
	log_file_location = None
	server_config_location = None
	gameplay_config_location = None
	welcome_message_location = None
	exit_message_location = None
	work_factor = None
	
	world_instance = None

	logger = None

	welcome_message_data = ''
	exit_message_data = ''
	
	pending_connection_list = [ ]
	# The difference between pending and established is that the pending clients still have yet to login while the established clients
	# have already verified.
	established_connection_list = [ ]
	
	version_major = 1
	version_minor = 0
	version_revision = 0
	
	def __init__(self, pid, config, data_path):
		self.pidfile = pid
		
		self.database_location = data_path + 'Database.db'
		self.log_file_location = data_path + 'log.txt'
		self.logger = log.Log(self.log_file_location, pid is None)

		self.server_config_location = 'config/settings_server.cfg'
		self.gameplay_config_location = 'config/settings_gameplay.cfg'
		self.welcome_message_location = 'config/welcome_message.txt'
		self.exit_message_location = 'config/exit_message.txt'
  
		self.server_settings = config
		self.work_factor = int(self.server_settings.get_index('WorkFactor'))
		
		try:
			with open(self.welcome_message_location) as f:
				for line in f:
					if (string.find(line, '\n') == -1):
						line = line + '\n'
					self.welcome_message_data += line
				f.close()
				self.welcome_message_data += '\n'
		except IOError as e:
			self.welcome_message_data = 'Unable to load welcome message!'
			
		try:
			with open(self.exit_message_location) as f:
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
		# This should actually have a use someday, it was intended on converting between certain string values to their proper
		# boolean values in server configuration files as all of it is loaded as string data.
		text_mappings = { 
			  'yes': True,
			  'y': True,
			  'no': False,
			  'n': False,
			  '1': True,
			  '0': False,
			  'nope': False,
			  'enable': True,
			  'enabled': True,
			  'disable': False,
			  'disabled': False
		}
		
		server_version_string = '%s.%s.%s' % (self.version_major, self.version_minor, self.version_revision)
		self.logger.write('Server Version: ' + server_version_string)
		database_exists = True
		try:
			with open(self.database_location) as f: pass
		except IOError as e:
			self.logger.write('This appears to be your first time running the ScalyMUCK server. We must initialise your database ...')
			database_exists = False

		self.database_engine = create_engine('sqlite:///' + self.database_location, echo=False)
		models.Base.metadata.create_all(self.database_engine)
		self.world_instance = world.World(self.database_engine)
		
		if (database_exists is False):
			self.initialise_database()
		
		self.telnet_server = TelnetServer(port=int(self.server_settings.get_index('ServerPort')),
					        address=self.server_settings.get_index('ServerAddress'),
					        on_connect = self.on_client_connect,
					        on_disconnect = self.on_client_disconnect,
					        timeout = 0.05)
		self.is_running = True
		
		self.initialise_mods()
		
		self.logger.write('\nScalyMUCK successfully initialised.')
	
	"""
	      server.initialise_mods
	      
	      This function is called internally; it's just here to separate logic a bit.
	"""
	def initialise_mods(self):
		self.logger.write('Checking for modifications ...\n')
		mod_list = modman.get_mod_list()
		for mod in mod_list:
			self.logger.write('Found modification: "' + mod + '"')
			mod_data = modman.load_mod(mod, self.logger)
			if (mod_data is not None):
				mod_version = '%s.%s.%s' % (str(mod_data.version_major), str(mod_data.version_minor), str(mod_data.version_revision))
				server_version = '%s.%s.%s' % (str(mod_data.server_version_major), str(mod_data.server_version_minor), str(mod_data.server_version_revision))
			
				self.logger.write('Name: ' + mod_data.name)
				self.logger.write('Author: ' + mod_data.author)
				self.logger.write('Version: ' + mod_version)
				self.logger.write('Server Version: ' + server_version)
				self.logger.write('Total commands: ' + str(len(mod_data.commands)))
				self.logger.write('Description: ' + mod_data.description)
			
				# FIXME: Make this pay attention to what mod loader version it's expecting, not server version
				if (mod_data.server_version_major != self.version_major):
					self.logger.write('*** Failed to load modification, version mismatch error.')
					return
				else:
					self.logger.write('Attempting to load modification ...')
					for command in mod_data.commands:
						print(command)
			self.logger.write(' ')
		
	
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
						player_hash = target_player.get_hash()
						if (player_hash == bcrypt.hashpw(password, player_hash) == player_hash):
							connection.send('Good login\n')
							connection.id = target_player.get_id()
							for player in self.established_connection_list:
								if (player.id == connection.id):
									# Fixme: This message isn't dispatched as telnet_server.poll is not called before the player is deactivated
									player.send('Your connection has been replaced.\n')
									player.deactivate()
									self.established_connection_list.remove(player)
									break;
							self.pending_connection_list.remove(connection)	
							self.established_connection_list.append(connection)
						else:
							connection.send('You have specified an invalid username/password combination.\n')
				elif (len(command_data) >= 3 and command_data[0].lower() != 'connect'):
					connection.send('You must use the "connect" command:\n')
					connection.send('connect <username> <password>\n')

		# With already connected clients, we'll now deploy the command interface.
		for connection in self.established_connection_list:
			if (connection.cmd_ready is True):
				data = connection.get_command()

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
