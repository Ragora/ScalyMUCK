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
import logging

import bcrypt
from blinker import signal
from miniboa import TelnetServer
from sqlalchemy import create_engine

import daemon
import game.models
from game import interface, world

class Server(daemon.Daemon):
	is_running = False
	is_daemon = False
	telnet_server = None
	logger = None
	connection_logger = None
	world = None
	interface = None
	work_factor = 10
	update_ms = 1000

	welcome_message_data = ''
	exit_message_data = ''
	
	pending_connection_list = [ ]
	established_connection_list = [ ]

	connect_signal = signal('post_client_connect')
	disconnect_signal = signal('pre_client_disconnect')
	authenticated_signal = signal('post_client_authenticated')
	update_signal = signal('world_tick')

	def __init__(self, pid, config, data_path):
		# self.pidfile = pid
		
		self.connection_logger = logging.getLogger('Connections')
		self.logger = logging.getLogger('Server')
  		
		try:
			with open('config/welcome_message.txt') as f:
				self.welcome_message_data = f.read()  + '\n'
		except IOError as e:
			self.welcome_message_data = 'Unable to load welcome message!'
			self.logger.warning('Unable to load welcome message!')
			self.logger.warning(str(e))
		try:
			with open('config/exit_message.txt') as f:
				self.exit_message_data = f.read() + '\n'
		except IOError as e:
			self.exit_message_data = 'Unable to load exit message!'
			self.logger.warning('Unable to load exit message!')
			self.logger.warning(str(e))

		database_location = data_path + config.get_index('TargetDatabase', str)
		database_exists = True
		try:
			with open(database_location) as f: pass
		except IOError as e:
			self.logger.info('This appears to be your first time running the ScalyMUCK server. We must initialise your database ...')
			database_exists = False

		database_type = string.lower(config.get_index('DatabaseType', str))
		if (database_type == 'sqlite'):
			database_engine = create_engine('sqlite:////' + database_location, echo=False)
		else:
			database = config.get_index('DatabaseName', str)
			user = config.get_index('DatabaseUser', str)
			password = config.get_index('DatabasePassword', str)
			database_engine = create_engine(database_type + '://' + user + ':' + password + '@' + database_location + '/' + database, echo=False)
			database_engine.connect()

		self.world = world.World(database_engine)
		self.interface = interface.Interface(config, self.world)

		game.models.Base.metadata.create_all(database_engine)
	
		self.work_factor = config.get_index('WorkFactor', int)
		if (database_exists is False):
			portal_room = self.world.create_room('Portal Room Main')
			raptor_jesus = self.world.create_player('RaptorJesus', 'ChangeThisPasswordNowPlox', self.work_factor, portal_room)
			raptor_jesus.set_is_admin(True, commit=False)
			raptor_jesus.is_owner = True
			raptor_jesus.set_is_super_admin(True)
			self.logger.info('The database has been successfully initialised.')
		
		self.telnet_server = TelnetServer(port=config.get_index('ServerPort', int),
						address=config.get_index('ServerAddress', str),
					        on_connect = self.on_client_connect,
					        on_disconnect = self.on_client_disconnect,
					        timeout = 0.05)
	
		self.logger.info('ScalyMUCK successfully initialised.')
		self.is_running = True
	
	def update(self):
		self.telnet_server.poll()
		
		for connection in self.pending_connection_list:
			if (connection.cmd_ready is True):
				data = connection.get_command()
				command_data = string.split(data, ' ')

				if (len(command_data) < 3):
					connection.send('You did not specify all of the required arguments.\n')
				elif (len(command_data) >= 3 and string.lower(command_data[0]) == 'connect'):
					name = string.lower(command_data[1])
					password = command_data[2]
					
					target_player = self.world.find_player(name=name)
					if (target_player is None):
						connection.send('You have specified an invalid username/password combination.\n')
					else:
						player_hash = target_player.hash
						if (player_hash == bcrypt.hashpw(password, player_hash) == player_hash):
							connection.id = target_player.id
							connection.player = target_player
							target_player.connection = connection

							# Check to see if we need to update their hash
							if (target_player.work_factor != self.work_factor):
								target_player.work_factor = self.work_factor
								target_player.set_password(password)
								self.logger.warning(target_player.display_name + ' had their account hash updated.')

							self.connection_logger.info('Client ' + connection.address + ':' + str(connection.port) + ' signed in as user ' + target_player.display_name + '.')
							self.authenticated_signal.send(None, sender=target_player)
							for player in target_player.location.players:
								if (player is not target_player):
									player.send(target_player.display_name + ' has connected.')

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
				elif (len(command_data) >= 3 and string.lower(command_data[0]) != 'connect'):
					connection.send('You must use the "connect" command:\n')
					connection.send('connect <username> <password>\n')

		# With already connected clients, we'll now deploy the command interface.
		for connection in self.established_connection_list:
			input = connection.get_command()
			if (input is not None):
				self.interface.parse_command(connection.player, input)

			
	def shutdown(self):
		self.is_running = False
		for connection in self.established_connection_list:
			connection.send('The server has been shutdown adruptly by the server owner.\n')
			connection.socket_send()
		
	def run(self):
	    while (self.is_running()):
		self.update()

	def is_active(self):
		return self.is_running

	def is_running(self):
		return self.is_running

	def on_client_connect(self, client):
		self.connection_logger.info('Received client connection from ' + client.address + ':' + str(client.port))
		client.send(self.welcome_message_data)
		self.pending_connection_list.append(client)
		self.connect_signal.send(sender=client)
	 
	def on_client_disconnect(self, client):
		self.disconnect_signal.send(sender=client)
		self.connection_logger.info('Received client disconnection from ' + client.address + ':' + str(client.port))
		if (client in self.pending_connection_list):
			self.pending_connection_list.remove(client)
		elif (client in self.established_connection_list):
			for player in client.player.location.players:
				if (player is not client.player):
					player.send(client.player.display_name + ' has disconnected.')
			self.established_connection_list.remove(client)
			client.player.connection = None
