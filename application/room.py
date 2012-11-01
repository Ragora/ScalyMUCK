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
	def __init__(self, world_instance, info):
		self.database_information = info
		self.database_engine = world_instance.database_engine
		self.world_instance = world_instance
		
		def receive_event(self, database_engine, event_info):
			return
		
		def update(self):
			if (self.database_information is not None):
				instance = self.world_instance.find_room(name=self.database_information.name)
				self.database_information.id = instance.get_id()
				return True
			else:
				return False