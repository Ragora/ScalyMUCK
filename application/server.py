"""
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
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.reflection import Inspector

import daemon
import game.models
from game import interface, world

class Server(daemon.Daemon):
	""" 

	Server class that is initialized by the main.py script to act as the MUCK server.
	It performs all of the core functions of the MUCK server, which is mainly accepting
	connections and performing the login sequence before giving them access to the
	server and its world.

	"""
	is_running = False
	telnet_server = None
	logger = None
	connection_logger = None
	world = None
	interface = None
	work_factor = 10

	welcome_message_data = 'Unable to load welcome message!\n'
	exit_message_data = 'Unable to load exit message!\n'
	
	pending_connection_list = [ ]
	established_connection_list = [ ]

	post_client_connect = signal('post_client_connect')
	pre_client_disconnect = signal('pre_client_disconnect')
	post_client_authenticated = signal('post_client_authenticated')
	world_tick = signal('world_tick')

	auth_low_argc = None
	auth_invalid_combination = None
	auth_connected = None
	auth_replace_Connection = None
	auth_connection_replaced = None
	auth_connect_suggestion = None
	game_client_disconnect = None

	def __init__(self, config=None, path=None, workdir=None):
		""" The server class is created and managed by the main.py script.

		When created, the server automatically initiates a Telnet server provided
		by Miniboa which immediately listens for incoming connections and will query
		them for login details upon connection.

		Keyword arguments:
			config -- An instance of game.Settings that is to be used when loading configuration data.
			path -- The data path that all permenant data should be written to.
			workdir -- The current working directory of the server. This should be an absolute path to application/.
	 
		"""
		self.connection_logger = logging.getLogger('Connections')
		self.logger = logging.getLogger('Server')

		# Loading all of the configuration variables
		database_type = string.lower(config.get_index(index='DatabaseType', datatype=str))
		database = config.get_index(index='DatabaseName', datatype=str)
		user = config.get_index(index='DatabaseUser', datatype=str)
		password = config.get_index(index='DatabasePassword', datatype=str)
		self.work_factor = config.get_index(index='WorkFactor', datatype=int)
		if (database_type == 'sqlite'):
			database_location = path + config.get_index(index='TargetDatabase', datatype=str)
		else:
			database_location = config.get_index(index='TargetDatabase', datatype=str)

		# Load server messages
		self.auth_low_argc = config.get_index('AuthLowArgC', str)
		self.auth_invalid_combination = config.get_index('AuthInvalidCombination', str)
		self.auth_connected = config.get_index('AuthConnected', str)
		self.auth_replace_connection = config.get_index('AuthReplaceConnection', str)
		self.auth_connection_replaced = config.get_index('AuthConnectionReplaced', str)
		self.auth_connect_suggestion = config.get_index('AuthConnectSuggestion', str).replace('\\n','\n')
		self.auth_replace_connection_global = config.get_index('AuthReplaceConnectionGlobal', str)
		self.game_client_disconnect = config.get_index('GameClientDisconnect', str)
  		
		# Loading welcome/exit messages
		with open(workdir + 'config/welcome_message.txt') as f:
			self.welcome_message_data = f.read()  + '\n'
		with open(workdir + 'config/exit_message.txt') as f:
			self.exit_message_data = f.read() + '\n'

		# Connect/Create our database is required
		database_exists = True
		if (database_type == 'sqlite'):
			try:
				with open(database_location) as f: pass
			except IOError as e:
				self.logger.info('This appears to be your first time running the ScalyMUCK server. We must initialise your database ...')
				database_exists = False

			database_engine = create_engine('sqlite:////%s' % (database_location), echo=False)
		else:
			url = database_type + '://' + user + ':' + password + '@' + database_location + '/' + database
			try:
				database_engine = create_engine(url, echo=False)
				connection = database_engine.connect()
			except OperationalError as e:
				self.logger.error(str(e))
				self.logger.error('URL: ' + url)
				self.is_running = False
				return

		self.world = world.World(database_engine)
		self.interface = interface.Interface(config=config, world=self.world, workdir=workdir, session=self.world.session, server=self)
		game.models.Base.metadata.create_all(database_engine)
	
		# Check to see if our root user exists
		if (database_type != 'sqlite'):
			root_user = self.world.find_player(name='RaptorJesus')
			if (root_user is None):
				database_exists = False

		game.models.server = self
		game.models.world = self.world

		if (database_exists is False):
			room = self.world.create_room('Portal Room Main')
			user = self.world.create_player(name='RaptorJesus', password='ChangeThisPasswordNowPlox', workfactor=self.work_factor, location=room, admin=True, sadmin=True, owner=True)
			room.set_owner(user)
			self.logger.info('The database has been successfully initialised.')
		
		self.telnet_server = TelnetServer(port=config.get_index(index='ServerPort', datatype=int),
						address=config.get_index(index='ServerAddress', datatype=str),
					        on_connect = self.on_client_connect,
					        on_disconnect = self.on_client_disconnect,
					        timeout = 0.05)
	
		self.logger.info('ScalyMUCK successfully initialised.')
		self.is_running = True
	
	def update(self):
		""" The update command is called by the main.py script file.

		The update command does as it says, it causes the server to go through and
		poll for data from any of the clients and processes this data differently
		based on whether or not that they had actually logged in. When this function
		finishes calling, a single world tick has passed.

		"""
		try:
			self.telnet_server.poll()
		except UnicodeDecodeError:
			return
		
		for connection in self.pending_connection_list:
			if (connection.cmd_ready is True):
				data = "".join(filter(lambda x: ord(x)<127 and ord(x)>31, connection.get_command()))
				command_data = string.split(data, ' ')

				# Try and perform the authentification process
				if (len(command_data) < 3):
					connection.send('%s\n' % (self.auth_low_argc))
				elif (len(command_data) >= 3 and string.lower(command_data[0]) == 'connect'):
					name = string.lower(command_data[1])
					password = command_data[2]
					
					target_player = self.world.find_player(name=name)
					if (target_player is None):
						connection.send('%s\n' % self.auth_invalid_combination)
					else:
						player_hash = target_player.hash
						if (player_hash == bcrypt.hashpw(password, player_hash) == player_hash):
							connection.id = target_player.id
							target_player.connection = connection

							# Check if our work factors differ
							work_factor = int(player_hash.split('$')[2])
							if (work_factor != self.work_factor):
								target_player.set_password(password)
								self.logger.info('%s had their hash updated.' % (target_player.display_name))

							self.connection_logger.info('Client %s:%u signed in as user %s.' % (connection.address, connection.port, target_player.display_name))
							self.post_client_authenticated.send(None, sender=target_player)
							for player in target_player.location.players:
								if (player is not target_player):
									player.send(self.auth_connected % target_player.display_name)

							for player in self.established_connection_list:
								if (player.id == connection.id):
									player.send('%s\n' % self.auth_replace_connection)
									player.socket_send()
									player.deactivate()
									player.sock.close()
									connection.send('%s\n' % self.auth_connection_replaced)
									self.world.find_room(id=target_player.location_id).broadcast(self.auth_replace_connection_global % target_player.display_name, target_player)
									self.established_connection_list.remove(player)
									break
							self.pending_connection_list.remove(connection)	
							self.established_connection_list.append(connection)
						else:
							connection.send('You have specified an invalid username/password combination.\n')
				elif (len(command_data) >= 3 and string.lower(command_data[0]) != 'connect'):
					connection.send('%s\n' % (self.auth_connect_suggestion))
					#connection.send('You must use the "connect" command:\n')
					#connection.send('connect <username> <password>\n')

		# With already connected clients, we'll now deploy the command interface.
		for connection in self.established_connection_list:
			if (connection.cmd_ready):
				input = "".join(filter(lambda x: ord(x)<127 and ord(x)>31, connection.get_command()))
				sending_player = self.world.find_player(id=connection.id)
				sending_player.connection = connection
				self.interface.parse_command(sender=sending_player, input=input)

		self.world_tick.send(None)

	def shutdown(self):
		""" Shuts down the ScalyMUCK server.

		This command shuts down the ScalyMUCK server and gracefully disconnects all connected clients
		by sending a message before their disconnection which currently reads: "The server has been shutdown
		adruptly by the server owner." This message cannot be changed.

		"""	
		self.is_running = False
		for connection in self.established_connection_list:
			connection.send('The server has been shutdown adruptly by the server owner.\n')
			connection.socket_send()

	def find_connection(self, id):
		""" Finds a player connection by their database ID. """
		for player in self.established_connection_list:
			if (player.id == id):
				return player

	def on_client_connect(self, client):
		""" This is merely a callback for Miniboa to refer to when receiving a client connection from somewhere. """
		self.connection_logger.info('Received client connection from %s:%u' % (client.address, client.port))
		client.send(self.welcome_message_data)
		self.pending_connection_list.append(client)
		self.post_client_connect.send(sender=client)

	def on_client_disconnect(self, client):
		""" This is merely a callback for Miniboa to refer to when receiving a client disconnection. """
		self.pre_client_disconnect.send(sender=client)
		self.connection_logger.info('Received client disconnection from %s:%u' % (client.address, client.port))
		# Iterate over anyone who had connected but did not authenticate
		if (client in self.pending_connection_list):
			self.pending_connection_list.remove(client)
		# Otherwise run over the list of people who had authenticated
		elif (client in self.established_connection_list):
			player = self.world.find_player(id=client.id)
			room = self.world.find_room(id=player.location_id)
			room.broadcast(self.game_client_disconnect % player.display_name, player)

			self.established_connection_list.remove(client)
