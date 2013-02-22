"""
      world.py
      Game world code for ScalyMUCK
      Copyright (c) 2012 Liukcairo
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import ai
import room
import player
import item
import models

class World():
	database_engine = None
	
	def __init__(self, engine):
		self.database_engine = engine
		return
	      
	def create_room(self, name, description='<Unset>'):
		database_session = scoped_session(sessionmaker(bind=self.database_engine))
		room_data = models.Room(name, description)
		database_session.add(room_data)
		database_session.commit()
		room_data = database_session.query(models.Room).filter_by(name=name).first()
		room_instance = room.Room(self, room_data)
		return room_instance
	      
	def find_room(self, id=None, name=None):
		if (name is None and id is None):
			return
		  
		target_room = None
		database_session = scoped_session(sessionmaker(bind=self.database_engine)) 
		if (name is not None):
			target_room_data = database_session.query(models.Room).filter_by(name=name).first()
			if (target_room_data is not None):
				target_room = Room(self, target_room_data)
		else:
			target_room_data = database_session.query(models.Room).filter_by(id=id).first()
			if (target_room_data is not None):
				target_room = Room(self, target_room_data)
				
		return target_room
	
	def create_player(self, name, password, work_factor, location):
		database_session = scoped_session(sessionmaker(bind=self.database_engine))
		player_inventory = self.create_room(name + "'s Inventory")	
			
		database_information = models.Player(name, password, work_factor, location.get_id(), player_inventory.get_id())
		database_session.add(database_information)
		database_session.commit()
		player_data = database_session.query(models.Player).filter_by(name=name,hash=database_information.hash).first()
		player_instance = player.Player(self, player_data)
		return player_instance
	      
	def find_player(self,id=None,name=None):
		if (name is None and id is None):
			return None
 
		target_player = None
		database_session = scoped_session(sessionmaker(bind=self.database_engine))     
		if (name is not None):
			target_player_data = database_session.query(models.Player).filter_by(name=name).first()
			if (target_player_data is not None):
				target_player = player.Player(self, target_player_data)
		else:
			target_player_data = database_session.query(models.Player).filter_by(id=id).first()
			if (target_player_data is not None):
				target_player = player.Player(self, target_player_data)

		return target_player
