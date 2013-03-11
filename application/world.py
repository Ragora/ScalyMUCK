"""
	world.py

	Game world code for ScalyMUCK
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import Room, Player, Item

class World():
	database_engine = None
	database_session = None
	
	_cached_players = [ ]
	_cached_items = [ ]
	_cached_rooms = [ ]
	def __init__(self, engine):
		self.database_engine = engine
		self.database_session = scoped_session(sessionmaker(bind=self.database_engine))
		return
	      
	def create_room(self, name, description='<Unset>', owner=0):
		room = Room(name, description, owner)
		room.world = self
		self.database_session.add(room)
		self.database_session.commit()

		self._cached_rooms.append(room)
		return room
	      
	def find_room(self, id=None, name=None):
		if (name is None and id is None):
			return

		for room in self._cached_rooms:
			if (room.id == id or room.name == name):
				return room

		if (name is not None):
			target_room = self.database_session.query.query(Room).filter_by(name=name).first()
			if (target_room is not None):
				target_room.world = self
				self._cached_rooms.append(target_room)
				return target_room 
		else:
			target_room = self.database_session.query(Room).filter_by(id=id).first()
			if (target_room is not None):
				target_room.world = self
				self._cached_rooms.append(target_room)
				return target_room
		return None
	
	def create_player(self, name, password, work_factor, location):
		player_inventory = self.create_room(name + "'s Inventory")	
			
		player = Player(name, password, work_factor, location.id, 0)
		player.world = self
		self.database_session.add(player)

		location.players.append(player)
		self.database_session.add(location)

		self.database_session.add(player_inventory)
		self.database_session.commit()
		
		player.location = location
		self._cached_players.append(player)
		return player
	      
	def find_player(self,id=None,name=None,display_name=None):
		if (name is None and id is None):
			return None

		for player in self._cached_players:
			if (player.id == id or player.name == name or player.display_name == display_name):
				return player
				 
		if (name is not None):
			target_player = self.database_session.query(Player).filter_by(name=name).first()
			if (target_player is not None):
				target_player.world = self
				self._cached_players.append(target_player)
				target_player.location = self.database_session.query(Room).filter_by(id=target_player.location_id).first()
				return target_player
		else:
			target_player = self.database_session.query(Player).filter_by(id=id).first()
			if (target_player is not None):
				target_player.world = self
				self._cached_players.append(target_player)
				target_player.location = self.database_session.query(Room).filter_by(id=target_player.location_id).first()
				return target_player
		return None
