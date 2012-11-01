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
	
	def __init__(self, world_instance, info):
		self.database_information = info
		self.database_engine = world_instance.database_engine
		self.world_instance = world_instance
	
	def update(self):
		if (self.database_information is not None):
			return
		return
	
	def get_hash(self):
		if (self.database_information is not None):
			return self.database_information.hash
		else:
			return None
	      
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