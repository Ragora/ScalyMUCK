"""
    player.py
    Player class
    Copyright (c) 2012 Liukcairo
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import models
import killable

class Player(killable.Killable):
	def __init__(self, database_engine, search_id=None, search_name=None, info=None):
		self.database_engine = database_engine
		if (search_id is None and search_name is None and info is None):
			return
 
		database_session = scoped_session(sessionmaker(bind=self.database_engine))     
		if (info is not None):
			self.database_information = info
		elif (search_name is not None):
			target_player_data = database_session.query(models.Player).filter_by(name=search_name).first()
			self.database_information = target_player_data
		else:
			target_player_data = database_session.query(models.Player).filter_by(id=search_id).first()
			self.database_information = target_player_data

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

	      
def new(name, password, work_factor, location, database_engine):
	database_session = scoped_session(sessionmaker(bind=database_engine))
	player_db = models.Player(name, password, work_factor, location)
	database_session.add(player_db)
	database_session.commit()
	
	player_instance = Player(database_engine, info=player_db)
	return player_instance