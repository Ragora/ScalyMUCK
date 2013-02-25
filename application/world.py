"""
      world.py
      Game world code for ScalyMUCK
      Copyright (c) 2012 Liukcairo
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import Room, Player, Item

class World():
	database_engine = None
	
	_cached_players = [ ]
	_cached_items = [ ]
	_cached_rooms = [ ]
	def __init__(self, engine):
		self.database_engine = engine
		return
	      
	def create_room(self, name, description='<Unset>'):
		database_session = scoped_session(sessionmaker(bind=self.database_engine))
		room = Room(name, description)
		database_session.add(room)
		database_session.commit()

		self._cached_rooms.append(room)
		return room
	      
	def find_room(self, id=None, name=None):
		if (name is None and id is None):
			return

		for room in self._cached_rooms:
			if (room.id == id or room.name == name):
				return room

		database_session = scoped_session(sessionmaker(bind=self.database_engine)) 
		if (name is not None):
			target_room = database_session.query(Room).filter_by(name=name).first()
			if (target_room is not None):
				self._cached_rooms.append(target_room)
				return target_room 
		else:
			target_room = database_session.query(Room).filter_by(id=id).first()
			if (target_room is not None):
				self._cached_rooms.append(target_room)
				return target_room
		return None
	
	def create_player(self, name, password, work_factor, location):
		database_session = scoped_session(sessionmaker(bind=self.database_engine))
		# player_inventory = self.create_room(name + "'s Inventory")	
			
		player = Player(name, password, work_factor, location.id, 0)
		database_session.add(player)

		location.players.append(player)
		database_session.add(location)

		# database_session.add(player_inventory)
		database_session.commit()
		
		player.location = location
		self._cached_players.append(player)
		return player
	      
	def find_player(self,id=None,name=None,display_name=None):
		if (name is None and id is None):
			return None

		for player in self._cached_players:
			if (player.id == id or player.name == name or player.display_name == display_name):
				return player
				
		database_session = scoped_session(sessionmaker(bind=self.database_engine))     
		if (name is not None):
			target_player = database_session.query(Player).filter_by(name=name).first()
			if (target_player is not None):
				self._cached_players.append(target_player)
				target_player.location = database_session.query(Room).filter_by(id=target_player.location_id).first()
				return target_player
		else:
			target_player = database_session.query(Player).filter_by(id=id).first()
			if (target_player is not None):
				self._cached_players.append(target_player)
				target_player.location = database_session.query(Room).filter_by(id=target_player.location_id).first()
				return target_player
		return None
