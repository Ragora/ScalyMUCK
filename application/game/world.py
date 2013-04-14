"""
	world.py

	Game world code for ScalyMUCK. This contains "global" functions that is to
	be called by the various mods of the MUCK to perform actions such as creating
	Players.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import Room, Player, Item
import exception

class World():
	"""

	The "singleton" class that represents the ScalyMUCK world in memory and is to
	be passed to every mod that actually manages to initialize when loaded.
	
	"""
	engine = None
	session = None
	
	cached_players = [ ]
	cached_items = [ ]
	cached_rooms = [ ]
	cached_exits = [ ]

	def __init__(self, engine):
		""" Initializes an instance of the World with an SQLAlchemy engine. """
		self.engine = engine
		self.session = scoped_session(sessionmaker(bind=self.engine))
		return
	      
	def create_room(self, name, description='<Unset>', owner=0):
		""" Creates a new Room if the World.

		Keyword arguments:
			description -- The description that is to be used with the new Room instance.
			owner -- The ID or instance of Player that is to become the owner of this Room.

		"""
		room = Room(name, description, owner)
		room.world = self
		self.session.add(room)
		self.session.commit()

		self.cached_rooms.append(room)
		return room
	      
	# TODO: This code is pretty screwy, I think I need to redo it.
	def find_room(self, id=None, name=None):
		""" Locates the specified Room in the ScalyMUCK world.

		This can be a bit computionally intense if you are running a very large world.

		Keyword arguments (one or the other):
			id -- The id of the requested room to return an instance of. This overrides the name if both are specified.
			name -- The name of the requested room to return an instance of.

		"""
		if (name is None and id is None):
			raise exception.WorldArgumentError('Neither an id nor a name was specified to find_room. (or None was passed in)')

		for room in self.cached_rooms:
			if (room.id == id or room.name == name):
				return room

		if (id is not None):
			target_room = self.session.query(Room).filter_by(id=id).first()
			if (target_room is not None):
				target_room.world = self
				self.cached_rooms.append(target_room)

				for item in target_room.items:
					if (self.item_loaded(item.id) is False):
						self.cached_items.append(item)
				for player in target_room.players:
					if (self.player_loaded(player.id) is False):
						self.cached_players.append(player)
				for exit in target_room.exits:
					if (self.exit_loaded(exit.id) is False):
						self.cached_exits.append(exit)
				return target_room
		elif (name is not None):
			target_room = self.session.query.query(Room).filter_by(name=name).first()
			if (target_room is not None):
				target_room.world = self
				self.cached_rooms.append(target_room)
				
				for item in target_room.items:
					if (self.item_loaded(item.id) is False):
						self.cached_items.append(item)
				for player in target_room.players:
					if (self.player_loaded(player.id) is False):
						self.cached_players.append(player)
				for exit in target_room.exits:
					if (self.exit_loaded(exit.id) is False):
						self.cached_exits.append(exit)
						if (self.room_loaded(exit.target_id)):
							exit.target = self.find_room(id=exit.target_id)
						else:
							exit.target = self.session.query.query(Room).filter_by(id=exit.target_id).first()
							self.cached_rooms.append(exit.target)
				return target_room
		else:
			return None
	
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

		if (type(location) is int):
			location = self.find_room(id=location)

		player_inventory = self.create_room(name + "'s Inventory")				
		player = Player(name, password, workfactor, location.id, 0, admin=admin, sadmin=sadmin, owner=owner)
		player.world = self
		player.inventory_id = player_inventory.id
		self.session.add(player)

		location.players.append(player)
		self.session.add(location)

		self.session.add(player_inventory)
		self.session.commit()
		
		player.location = location
		player.inventory = player_inventory
		self.cached_players.append(player)
		self.cached_rooms.append(player_inventory)
		return player

	# TODO: This code is pretty screwy, I think I need to redo it.
	def find_player(self,id=None,name=None):
		""" Locates a Player inside of the ScalyMUCK world.

		This searches the entire WORLD for the specified Player so if you happen to be running a very, very
		large world this search will end up getting slow and it is recommended in that case that you try and
		use the Room level find_player function whenever possible.

		Keyword arguments (one or the other):
			id -- The ID of the Player to locate. This overrides the name if both are specified.
			name -- The name of the Player to locate.
		
		"""
		if (name is None and id is None):
			raise exception.WorldArgumentError('No id or name specified. (or both were None)')

		for player in self.cached_players:
			if (player.id == id or player.name == name):
				return player
			
		if (id is not None):
			target_player = self.session.query(Player).filter_by(id=id).first()
			if (target_player is not None):
				target_player.world = self
				self.cached_players.append(target_player)
				if (self.room_loaded(target_player.location_id) is False):
					target_player.location = self.session.query(Room).filter_by(id=target_player.location_id).first()
					self.cached_rooms.append(target_player.location)
				else:
					target_player.location = self.find_room(id=target_player.location_id)

				if (self.room_loaded(target_player.inventory_id) is False):
					target_player.inventory = self.session.query(Room).filter_by(id=target_player.inventory_id).first()
					self.cached_rooms.append(target_player.inventory)
				else:
					target_player.inventory = self.find_room(id=target_player.inventory_id)
				return target_player	 
		elif (name is not None):
			target_player = self.session.query(Player).filter_by(name=name).first()
			if (target_player is not None):
				target_player.world = self
				self.cached_players.append(target_player)
				if (self.room_loaded(target_player.location_id) is False):
					target_player.location = self.session.query(Room).filter_by(id=target_player.location_id).first()
					self.cached_rooms.append(target_player.location)
				else:
					target_player.location = self.find_room(id=target_player.location_id)
				if (self.room_loaded(target_player.inventory_id) is False):
					target_player.inventory = self.session.query(Room).filter_by(id=target_player.inventory_id).first()
					self.cached_rooms.append(target_player.inventory)
				else:
					target_player.inventory = self.find_room(id=target_player.inventory_id)
				return target_player
		else:
			return None

	def get_players(self):
		""" Returns a list of all Players in the ScalyMUCK world. """
		list = [ ]
		results = self.session.query(Player).filter_by()
		for player in results:
			load_test = self.find_player(id=player.id)
			if (load_test is None):
				list.append(self.find_player(id=player.id))
				self.cached_players.append(player)
			else:
				list.append(load_test)
		return list

	def find_item(self, id):
		""" Locates an item by it's ID number.

		If the ID number does not exist then None is returned.

		"""
		if (id is None):
			raise exception.WorldArgumentError('No ID was specified. (or it was None')

		for item in self.cached_items:
			if (item.id == id):
				return item

		target_item = self.session.query(Item).filter_by(id=id).first()
		if (target_item is not None):
			target_item.location = self.session.query(Room).filter_by(id=target_item.location_id).first()
			target_item.world = self
			return target_item

	def create_item(self, name=None, description='<Unset>', owner=0, location=None):
		""" Creates a new item in the ScalyMUCK world.

		Keyword arguments:
			name -- The name of the Item that is to be used.
			description -- The description of the Item that is to be used. Default: <Unset>
			owner -- The ID or instanceo of Player that is to become the owner of this Item.
			location -- The ID or instance of Room that is to become the location of this Item.
		"""
		if (name is None or location is None):
			raise exception.WorldArgumentError('Either the name or location was not specified. (or they were None)')

		item = Item(name, description, owner)
		if (type(location) is int):
			item.location_id = location
			item.location = self.session.query(Room).filter_by(id=location).first()
		else:
			item.location = location
			item.location_id = location.id

		item.world = self
		self.session.add(item)
		self.session.commit()

		self.cached_items.append(item)
		return item

	def item_loaded(self, id):
		""" Checks whether or not an Item is loaded into memory by ID. """
		for item in self.cached_items:
			if (item.id == id):
				return True
		return False

	def player_loaded(self, id=None, name=None):
		""" Checks whether or not a Player is loaded into memory by ID or name. 

		Keyword arguments:
			id -- The ID of the Player to check that is loaded. This overrides the name if both are specified.
			name -- The name of the Player to check that is loaded.

		"""
		if (id is None and name is None):
			raise exception.WorldArgumentError('No id or name specified. (or both were None)')

		if (id is not None):
			for player in self.cached_players:
				if (player.id == id):
					return True
		else:
			for player in self.cached_players:
				if (player.name == name):
					return True
		return False

	def room_loaded(self, id):
		""" Checks whether or not a Room is loaded into memory by ID. """
		for room in self.cached_rooms:
			if (room.id == id):
				return True
		return False

	def exit_loaded(self, id):
		""" Checks whether or not an Exit is loaded into memory by ID. """
		for exit in self.cached_exits:
			if (exit.id == id):
				return True
		return False
