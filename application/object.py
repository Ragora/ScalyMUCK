"""
    object.py
    Base class for things that may be contained inside
    of a container in ScalyMUCK
    Copyright (c) 2012 Liukcairo
"""

import base
import models
import room

class Object(base.Base):
	location = None
	def __init__(self):
		return
	
	def set_location(database_engine, name=None,id=None):
		if (name is None and id is None):
			return
		return