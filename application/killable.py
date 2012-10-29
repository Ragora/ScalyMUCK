"""
    killable.py
    Base class for things in ScalyMUCK that can
    die.
    Copyright (c) 2012 Liukcairo
"""

import object

class Killable(object.Object):
	name = None
	description = None
	
	hp = 0
	strength = 0
	dexterity = 0
	# Dimwit
	intelligence = 0
	
	def __init__(self):
		return
