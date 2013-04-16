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

from models import Room, Player, Item, Bot
import exception

class World():
	"""

	The "singleton" class that represents the ScalyMUCK world in memory and is to
	be passed to every mod that actually manages to initialize when loaded.
	
	"""
	engine = None
	session = None
	
	def __init__(self, engine):
		""" Initializes an instance of the World with an SQLAlchemy engine. """
		self.engine = engine
		self.session = scoped_session(sessionmaker(bind=self.engine))
	      
	def create_room(self, name, description='<Unset>', owner=0):
		""" Creates a new Room if the World.

		Keyword arguments:
			description -- The description that is to be used with the new Room instance.
			owner -- The ID or instance of Player that is to become the owner of this Room.

		"""
		room = Room(name, description, owner)
		self.session.add(room)
		self.session.commit()
		self.session.refresh(room)
		return room
	      
	def find_room(self, id=None, name=None):
		""" Locates the specified Room in the ScalyMUCK world.

		This can be a bit computionally intense if you are running a very large world.

		Keyword arguments (one or the other):
			id -- The id of the requested room to return an instance of. This overrides the name if both are specified.
			name -- The name of the requested room to return an instance of.

		"""
		if (name is None and id is None):
			raise exception.WorldArgumentError('Neither an id nor a name was specified to find_room. (or None was passed in)')

		if (id is not None):
			target_room = self.session.query(Room).filter_by(id=id).first()
		elif (name is not None):
			target_room = self.session.query.query(Room).filter_by(name=name).first()

		return target_room
	
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
		player.inventory_id = player_inventory.id
		self.session.add(player)

		location.players.append(player)
		self.session.add(location)

		self.session.add(player_inventory)
		self.session.commit()

		self.session.refresh(player)
		self.session.refresh(player_inventory)
		
		player.location = location
		player.inventory = player_inventory
		return player

	def create_bot(self, name=None, location=None):
		""" Creates a new instance of a Bot.

		Keyword arguments:
			name -- The name of the new Player instance to be used.
			location -- The ID or instance of Room that the new Player is to be created at.

		"""
		if (name is None or location is None):
			raise exception.WorldArgumentError('All of the arguments to create_bot are mandatory! (or None was passed in)')

		if (type(location) is int):
			location = self.find_room(id=location)
			
		bot = bot(name, '<Unset>', location)
		self.session.add(bot)
		location.bots.append(bot)
		self.session.add(location)
		self.session.commit()

		self.session.refresh(bot)
		
		bot.location = location
		return bot

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

		if (id is not None):
			target_player = self.session.query(Player).filter_by(id=id).first()
		elif (name is not None):
			target_player = self.session.query(Player).filter_by(name=name).first()

		if (target_player is not None):
			target_player.location = self.find_room(id=target_player.location_id)
			target_player.inventory = self.find_room(id=target_player.inventory_id)

		return target_player

	def find_bot(self,id=None):
		""" Locates a Bot inside of the ScalyMUCK world.

		This searches the entire WORLD for the specified Bot so if you happen to be running a very, very
		large world this search will end up getting slow and it is recommended in that case that you try and
		use the Room level find_player function whenever possible.

		Keyword arguments (one or the other):
			id -- The ID of the Bot to locate. This overrides the name if both are specified.
		
		"""
		if (id is None):
			raise exception.WorldArgumentError('No id or name specified. (or both were None)')

		if (id is not None):
			target_bot = self.session.query(Bot).filter_by(id=id).first()

		if (target_bot is not None):
			target_bot.location = self.find_room(id=target_bot.location_id)

		return target_bot

	def get_players(self):
		""" Returns a list of all Players in the ScalyMUCK world. """
		list = [ ]
		results = self.session.query(Player).filter_by()
		for player in results:
			load_test = self.find_player(id=player.id)
			if (load_test is None):
				list.append(self.find_player(id=player.id))
			else:
				list.append(load_test)
		return list

	def find_item(self, id):
		""" Locates an item by it's ID number.

		If the ID number does not exist then None is returned.

		"""
		if (id is None):
			raise exception.WorldArgumentError('No ID was specified. (or it was None')

		target_item = self.session.query(Item).filter_by(id=id).first()
		if (target_item is not None):
			target_item.location = self.find_room(id=target_item.location_id)
			return target_item

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

		item = Item(name, description, owner)
		if (type(location) is int):
			item.location_id = location
			item.location = self.find_room(id=location)
		else:
			item.location = location
			item.location_id = location.id

		self.session.add(item)
		self.session.commit()
		self.session.refresh(item)
		return item
