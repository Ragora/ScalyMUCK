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
	def __init__(self, database_engine, name, info=None):
		if (info is None):
			database_session = scoped_session(sessionmaker(bind=database_engine))
			room_data = models.Room(name)
			database_session.add(room_data)
			database_session.commit()
			self.database_information = room_data
		else:
			self.database_information = info
		  
		self.database_engine = database_engine
		
		def receive_event(self, database_engine, event_info):
			return


def find(database_engine, name=None, id=None):
	if (name is None and id is None):
		return
		  
	target_room = None
	database_session = scoped_session(sessionmaker(bind=database_engine)) 
	if (name is not None):
		target_room_data = database_session.query(models.Room).filter_by(name=name).first()
		if (target_room_data is not None):
			target_room = Room(database_engine, None, info=target_room_data)
	else:
		target_room_data = database_session.query(models.Room).filter_by(id=id).first()
		if (target_room_data is not None):
			target_room = Room(database_engine, None, info=target_room_data)
			
	return target_room