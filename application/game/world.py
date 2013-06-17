""" 
	This contains "global" functions that is to
	be called by the various mods of the MUCK to perform actions such as creating
	Players.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import sqlalchemy.orm
from blinker import signal
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, scoped_session

import exception
from models import Room, Player, Item, Bot

class FakeConnection:
	closed = True
	def close(self):
		return

class World():
	"""

	The "singleton" class that represents the ScalyMUCK world in memory and is to
	be passed to every mod that actually manages to initialize when loaded.
	
	"""
	engine = None
	session = None
	fake_connection = FakeConnection()
	database_status = signal('database_status')
	
	def __init__(self, engine=None, server=None):
		""" Initializes an instance of the World with an SQLAlchemy engine. """
		self.engine = engine
		self.session = scoped_session(sessionmaker(bind=self.engine))
		self.server = server
		sqlalchemy.orm.Session = self.session
	      
	def create_room(self, name, description='<Unset>', owner=0):
		""" Creates a new Room if the World.

		Keyword arguments:
			description -- The description that is to be used with the new Room instance.
			owner -- The ID or instance of Player that is to become the owner of this Room.

		"""
		try:
			room = Room(name, description, owner)
			connection = self.connect()
			self.session.add(room)
			self.session.commit()
			self.session.refresh(room)
			room.session = self.session
			room.engine = self.engine
			connection.close()
			return room
		except OperationalError:
			self.session.rollback()
			raise exception.DatabaseError('Connection to the database server failed.')
	      
	def find_room(self, **kwargs):
		""" Locates the specified Room in the ScalyMUCK world.

		This can be a bit computionally intense if you are running a very large world.

		Keyword arguments (one or the other):
			id -- The id of the requested room to return an instance of. This overrides the name if both are specified.
			name -- The name of the requested room to return an instance of.

		"""
		connection = self.connect()
		try:
			target_room = self.session.query(Room).filter_by(**kwargs).first()

			if (target_room is not None):
				target_room.owner = self.session.query(Player).filter_by(id=target_room.owner_id).first()

				# Iterate and set all of our other custom attributes not defined by SQLAlchemy
				for item in target_room.items:
					item.location = target_room
					item.owner = self.session.query(Player).filter_by(id=item.owner_id).first()
					item.session = self.session
					item.engine = self.engine

				# NOTE: The above and below create separate Player instances, which hopefully both shouldn't be used within the same context ...
				for player in target_room.players:
					player.location = target_room
					player.inventory = self.session.query(Room).filter_by(id=player.inventory_id).first()
					player.session = self.session
					player.engine = self.engine

				for bot in target_room.bots:
					bot.location = target_room
					bot.session = self.session
					bot.engine = self.engine

			connection.close()
			return target_room
		except OperationalError:
			raise exception.DatabaseError('Connection to the database server failed.')
	
	def create_player(self, name=None, password=None, workfactor=None, location=None, admin=False, sadmin=False, owner=False):
		""" Creates a new instance of a Player.

		Keyword arguments:
			name -- The name of the new Player instance to be used.
			password -- The password that is to be used for the Player.
			workfactor -- The work factor # to be used when hasing the Player's password.
			location -- The ID or instance of Room that the new Player is to be created at.
			admin -- A boolean representing whether or not this new Player is an administrator.
			sadmin -- A boolean representing whether or not this new Player is a super administrator.
			owner -- A boolean representing whether or not this new Player is an owner.

		"""
		if (name is None or password is None or workfactor is None or location is None):
			raise exception.WorldArgumentError('All of the arguments to create_player are mandatory! (or None was passed in)')

		try:
			if (type(location) is int):
					location = self.find_room(id=location)

			player_inventory = self.create_room('%s\'s Inventory' % (name))		
			player = Player(name, password, workfactor, location.id, 0, admin=admin, sadmin=sadmin, owner=owner)
			player.inventory_id = player_inventory.id

			connection = self.connect()
			self.session.add(player)

			location.players.append(player)
			self.session.add(location)

			self.session.add(player_inventory)
			self.session.commit()

			self.session.refresh(player)
			self.session.refresh(player_inventory)
		
			player.location = location
			player.inventory = player_inventory
			player.session = self.session
			player.engine = self.engine
			player.location.session = self.session
			player.location.engine = self.engine
			player.inventory = player_inventory
			player_inventory.session = self.session
			player_inventory.engine = self.engine
			connection.close()
			return player
		except exception.DatabaseError:
			self.session.rollback()
			raise

	def create_bot(self, name=None, location=None):
		""" Creates a new instance of a Bot.

		Keyword arguments:
			name -- The name of the new Player instance to be used.
			location -- The ID or instance of Room that the new Player is to be created at.

		"""
		if (name is None or location is None):
			raise exception.WorldArgumentError('All of the arguments to create_bot are mandatory! (or None was passed in)')

		try:
			if (type(location) is int):
				location = self.find_room(id=location)
			
			bot = bot(name, '<Unset>', location)
			self.session.add(bot)
			location.bots.append(bot)
			self.session.add(location)
			self.session.commit()

			self.session.refresh(bot)
		
			bot.location = location
			bot.session = self.session
			bot.engine = self.engine
			return bot
		except OperationalError:
			self.session.rollback()
			raise exception.DatabaseError('Connection to the database server failed.')
		except exception.DatabaseError:
			self.session.rollback()
			raise

	def find_player(self, **kwargs):
		""" Locates a Player inside of the ScalyMUCK world.

		This searches the entire WORLD for the specified Player so if you happen to be running a very, very
		large world this search will end up getting slow and it is recommended in that case that you try and
		use the Room level find_player function whenever possible.

		Keyword arguments (one or the other):
			id -- The ID of the Player to locate. This overrides the name if both are specified.
			name -- The name of the Player to locate.
		
		"""
		connection = self.connect()
		try:
			target_player = self.session.query(Player).filter_by(**kwargs).first()

			if (target_player is not None):
				target_player.location = self.find_room(id=target_player.location_id)
				target_player.inventory = self.find_room(id=target_player.inventory_id)
				target_player.session = self.session
				target_player.engine = self.engine
			connection.close()
			return target_player
		except exception.DatabaseError:
			raise
		except OperationalError:
			raise exception.DatabaseError('Connection to the database server failed.')

	def find_bot(self, **kwargs):
		""" Locates a Bot inside of the ScalyMUCK world.

		This searches the entire WORLD for the specified Bot so if you happen to be running a very, very
		large world this search will end up getting slow and it is recommended in that case that you try and
		use the Room level find_player function whenever possible.

		Keyword arguments (one or the other):
			id -- The ID of the Bot to locate. This overrides the name if both are specified.
		
		"""
		connection = self.connect()
		try:
			target_bot = self.session.query(Bot).filter_by(**kwargs).first()

			if (target_bot is not None):
				target_bot.location = self.find_room(id=target_bot.location_id)
				target_bot.session = self.session
				target_bot.engine = self.engine
			connection.close()

			return target_bot
		except OperationalError:
			raise exception.DatabaseError('Connection to the database server failed.')
		except exception.DatabaseError:
			raise

	def get_players(self):
		""" Returns a list of all Players in the ScalyMUCK world. """
		list = [ ]
		connection = self.connect()
		try:
			results = self.session.query(Player).filter_by()
			for player in results:
				load_test = self.find_player(id=player.id)
				if (load_test is None):
					list.append(self.find_player(id=player.id))
				else:
					load_test.session = self.session
					load_test.engine = self.engine
			connection.close()
		except OperationalError:
			raise exception.DatabaseError('Connection to the database server failed.')
		except exception.DatabaseError:
			raise

		return list

	def find_item(self, **kwargs):
		""" Locates an item by any specifications.

		If the ID number does not exist then None is returned.

		"""
		connection = self.connect()
		try:
			target_item = self.session.query(Item).filter_by(**kwargs).first()
			if (target_item is not None):
				target_item.location = self.find_room(id=target_item.location_id)
				target_item.session = self.session
				target_item.engine = self.engine
			connection.close()

			return target_item
		except OperationalError:
			raise exception.DatabaseError('Connection to the database server failed.')
		except exception.DatabaseError:
			raise

	def create_item(self, name=None, description='<Unset>', owner=0, location=None):
		""" Creates a new item in the ScalyMUCK world.

		Keyword arguments:
			name -- The name of the Item that is to be used.
			description -- The description of the Item that is to be used. Default: <Unset>
			owner -- The ID or instance of Player that is to become the owner of this Item.
			location -- The ID or instance of Room that is to become the location of this Item.
		"""
		if (name is None or location is None):
			raise exception.WorldArgumentError('Either the name or location was not specified. (or they were None)')

		try:
			item = Item(name, description, owner)
			if (type(location) is int):
				item.location_id = location
				item.location = self.find_room(id=location)
			else:
				item.location = location
				item.location_id = location.id

			connection = self.connect()
			self.session.add(item)
			self.session.commit()
			self.session.refresh(item)
			item.session = self.session
			item.engine = self.engine
			connection.close()
			return item
		except OperationalError:
			self.session.rollback()
			raise exception.DatabaseError('Connection to the database server failed.')
		except exception.DatabaseError:
			self.session.rollback()
			raise

	def get_rooms(self, **kwargs):
		""" Returns all rooms in the database that meet the specified criterion.

		Keyword arguments:
			owner -- The owner we are to filter by. If not specified, this filter is not used.

		"""
		try:
			connection = self.connect()
			list = [ ]
			rooms = self.session.query(Room).filter_by(**kwargs)
			for room in rooms:
				list.append[self.find_room(id=room.id)]
				room.session = self.session
				room.engine = self.engine
			connection.close()
			return rooms
		except OperationalError:
			raise exception.DatabaseError('Connection to the database server failed.')
		except exception.DatabaseError:
			raise

	def connect(self):
		""" Establishes a connection to the database server. """
		try:
			connection = self.engine.connect()
		except OperationalError:
			self.database_status.send(sender=self, status=False)
			return self.fake_connection
		else:
			return connection
