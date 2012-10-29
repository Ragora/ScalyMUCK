"""
    base.py
    Base class for things in ScalyMUCK.
    Copyright (c) 2012 Liukcairo
"""

import models

class Base:
	database_information = None
	database_engine = None
	
	def __init__(self):
		return
	      
	def update(self):
		return
	      
	def get_id(self):
		if (self.database_information is not None):
			return self.database_information.id
		else:
			return None