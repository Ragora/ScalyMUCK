"""
    base.py
    Base class for things in ScalyMUCK.
    Copyright (c) 2012 Liukcairo
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import models

class Base:
	database_information = None
	database_engine = None
	
	def __init__(self):
		return

	"""
	    Base.get_id
	    
	    This is a function that is used to grab the id of this
	    object -- if it has any existing database information
	    that is.
	"""
	def get_id(self):
		if (self.exists() is True):
			return self.database_information.id
		else:
			return None
	
	"""
	    Base.exists
	    
	    This is a function that is used to check the existence
	    of any data base data on this class. Since the information
	    is None to start with and none of the child classes should
	    assign any data unless it actually exists in the database,
	    this should be left alone as it is.
	"""
	def exists(self):
		if (self.database_information is None):
			return False
		else:
			return True

	"""
	    Base.update
	    
	    This is a function that is used to signal to the object
	    that it must update it's information from the database.
	    
	    It is meant to be overriden by a child class.
	"""
	def update(self):
		return

	"""
	    Base.dump
	    
	    This is a function that dumps the class's current data
	    to specified database session but does not commit the
	    changes by itself. It's useful for saving everything
	    in the world so that many commits do not occur at
	    one given time but rather only once.
	    
	    It is meant to be overriden by a child class.
	"""
	def dump(self, database_session):
		return
	
	"""
	    Base.flush
	    
	    This is a function that performs the same as dump,
	    however the only difference is that it creates its
	    own database session and commits the changes itself.
	    
	    It is meant to be overridden by a child class.
	"""
	def flush(self):
		return
 
	"""
	    Base.receive_event
	    
	    This is a function called by blinker when an event is
	    received by this room.
	    
	    It is meant to be overridden by a child class.
	"""
	def receive_event(self, database_engine, event_info):
		return

	def set_name(self,new_name):
		return