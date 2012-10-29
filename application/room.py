"""
    room.py
    Room code for ScalyMUCK
    Copyright (c) 2012 Liukcairo
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import base
import models
import killable

class Room(base.Base):
	def __init__(self, database_engine, name_search=None, id_search=None, info=None):
		self.database_engine = database_engine
		if (name_search is None and id_search is None):
			return
		  
		database_session = scoped_session(sessionmaker(bind=self.database_engine)) 
		if (name_search is not None):
			target_room_data = database_session.query(models.Room).filter_by(name=name_search).first()
			self.database_information = target_room_data
		elif (info is not None):
			self.database_information = info
		else:
		      target_room_data = database_session.query(models.Room).filter_by(id=id_search).first()
		      self.database_information = target_room_data
	      
	def set_name(self,new_name):
		return

def new(name, database_engine):
	database_session = scoped_session(sessionmaker(bind=database_engine))
	room_db = models.Room(name)
	database_session.add(room_db)
	database_session.commit()
	
	room_instance = Room(database_engine, info=room_db)
	return room_instance