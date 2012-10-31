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
	
	"""
	    Object.set_location
	    
	    This is a function that is used to set the location
	    of which this object resides at.
	    
	    Optional arguments:
	    name -- If you know the name of the room, pass this in.
	    id -- If you know the id # of the room, pass this in.
	    room -- If you have an actual room object, pass it in.
	"""
	def set_location(name=None,id=None,room=None):
		if (name is None and id is None and room is None):
			return
		return