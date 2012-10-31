"""
    player.py
    Player class
    Copyright (c) 2012 Liukcairo
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import models
import killable
import room
import server

class Player(killable.Killable):
	connection = None
	
	def __init__(self, database_engine, name, password, work_factor, location, info=None):
		if (info is None):
			database_session = scoped_session(sessionmaker(bind=database_engine))
			player_inventory = models.Room(name + "'s Inventory")
			database_session.add(player_inventory)
			database_session.commit()
			
			player_inventory = room.find(database_engine, name=name + "'s Inventory")
			self.database_information = models.Player(name, password, work_factor, location.get_id(), player_inventory.get_id())
			database_session.add(self.database_information)
			database_session.commit()
		else:
			self.database_information = info
			
		self.database_engine = database_engine
	
	def update(self):
		if (self.database_information is not None):
			return
		return
	      
	"""
	    The following functions deal with manipulating any form of data
	    on this instance of player, such as the location or inventory
	    contents.
	"""
	      
	"""
	    The following functions deal with manipulating the administration
	    status of this instance of player.
	"""
	def set_admin(self, status):
		return
	
	def set_sadmin(self, status):
		return
	      
	def is_admin(self):
		return
	
	def is_sadmin(self):
		return
	      
	def is_owner(self):
		return

"""
    player.find
    
    This function is used to locate a player in the database by
    either their name or identification number. It returns none
    in the event nothing meets the criteria.
    
    Optional arguments:
    name -- If you know the name, pass this in.
    id -- If you know the id, pass this in.
"""
def find(database_engine, name=None, id=None):
	if (name is None and id is None):
		return None
 
	target_player = None
	database_session = scoped_session(sessionmaker(bind=database_engine))     
	if (search_name is not None):
		target_player_data = database_session.query(models.Player).filter_by(name=name).first()
		if (target_player_data is not None):
			target_player = Player(self.database_engine, None, None, None, None, info=target_player_data)
	else:
		target_player_data = database_session.query(models.Player).filter_by(id=id).first()
		if (target_player_data is not None):
			target_player = Player(self.database_engine, None, None, None, None, info=target_player_data)

	return target_player