"""
	server.py
	This is the main ScalyMUCK server code,
	it performs the initialisation of various
	systems and is the binding of everything.
	Copyright (c) 2012 Liukcairo
"""

import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from miniboa import TelnetServer
from os.path import expanduser

import models
import player
import room
import item
import settings
import daemon

class Server(daemon.Daemon):
	database_engine = None
	is_running = False
	is_daemon = False
	server_settings = None
	telnet_server = None
	
	home_directory = None
	database_location = None
	log_file_location = None
	server_config_location = None
	gameplay_config_location = None
	work_factor = None
	
	pending_connection_list = [ ]
	# The difference between pending and established is that the pending clients still have yet to login while the established clients
	# have already verified.
	established_connection_list = [ ]
	active_players = [ ]
	
	def __init__(self, pid):
		self.pidfile = pid
		
		self.home_directory = expanduser('~')
		self.database_location = self.home_directory + '/.scalyMUCK/Database.db'
		self.log_file_location = self.home_directory + '/.scalyMUCK/log.txt'
		self.server_config_location = self.home_directory + '/.scalyMUCK/settings_server.cfg'
		self.gameplay_config_location = self.home_directory + '/.scalyMUCK/settings_gameplay.cfg'
  
		self.server_settings = settings.Settings(self.server_config_location)
		self.work_factor = int(self.server_settings.get_index('WorkFactor'))

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
      
		file_handle = open(self.log_file_location, 'w')
		file_handle.write('ScalyMUCK Copyright (c) 2012 Liukcairo\n\n')
		file_handle.close()
		
		database_exists = True
		try:
			with open(self.database_location) as f: pass
		except IOError as e:
			self.write_log('This appears to be your first time running the ScalyMUCK server. We must initialise your database ...')
			database_exists = False
		
		self.database_engine = create_engine('sqlite:///' + self.database_location, echo=False)
		models.Base.metadata.create_all(self.database_engine)
		
		if (database_exists is False):
			self.initialise_database()
		
		self.telnet_server = TelnetServer(port=int(self.server_settings.get_index('ServerPort')),
					        address=self.server_settings.get_index('ServerAddress'),
					        on_connect = self.on_client_connect,
					        on_disconnect = self.on_client_disconnect,
					        timeout = 0.05)
		self.is_running = True
		self.write_log('ScalyMUCK successfully initialised.')

	def initialise_database(self):
		portal_room = room.new('Portal Room Main', self.database_engine)
		raptor_jesus = player.new('RaptorJesus', 'ChangeThisPasswordNowPlox', self.work_factor, portal_room.get_id(), self.database_engine)
		self.write_log('Database successfully initialised.')
		return
		
	def is_active(self):
		return self.is_running

	def write_log(self, data):
		file_handle = open(self.log_file_location, 'a')
		file_handle.write(data + '\n')
		print(data)
  
	def is_running(self):
		return self.is_running

	def update(self):
		self.telnet_server.poll()
		return

	def run(self):
	    self.initialise_server()
	    while (self.is_running()):
		self.update()

	# Miniboa Callbacks
	def on_client_connect(self, client):
		self.write_log('Received client connection from ' + client.address + ':' + str(client.port))

		return
	def on_client_disconnect(self, client):
		self.write_log('Received client disconnection from ' + client.address + ':' + str(client.port))
		return