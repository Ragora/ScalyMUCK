"""
	draakan.py

	Draakan implementation for the world generator.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

import game.models

from blinker import signal

# Species
class LimbFoot:
	""" Foot """
class LimbArm:
	""" Arm """
class LimbHand:
	""" Hand """
class LimbFinger:
	""" Finger """
class LimbToe:
	""" toe """
class LimbTorso:
	""" Torso """
class LimbLeg:
	""" Leg """
class LimbHead:
	""" head """
class TailUpper:
	""" Towards the body """
class TailLower:
	""" away from the body """

class SpeciesDraakan:
	""" Draakan Data """
	genders = [ GenderMale, GenderFemale ]
	weight = range(150,200) # Pounds
	height = range(66, 81) # Inches
	vore_weights = ( 90, 50 ) # Carnivore, Herbivore
	

	limbs = [ { 
			LimbTorso: { {
				LimbLeg: { {
				} }
			} }
		} ]
	def character_name_algorithm(self):
		return 'blah'

	def location_name_algorithm(self):
		return 'blah'

# Precoded Locations
class LocationDrasLeona:
	""" Draakan City """
	def child_locations(self):
		return [ (LocationDrasOutskirts, 1) ]

	def name_algorithm(self):
		return 'Dras-Leona'

class LocationDrasOutskirts:
	""" Outside of DrasLeona """
	def child_locations(self): return [ ]

	def name_algorithm(self):
		return 'Outskirts of Dras-Leona'

# Genders -- May be odd but this thing is to be as flexible as feasibly possible.
class GenderMale:
	""" Blah """

class GenderFemale:
	""" Blah """

# Groups
class GroupElite:
	""" Draakan Elites """

# Characters
class CharacterNyoka:
	""" Precoded Draakan Characters """
	name = 'Nyoka'
	species = SpeciesDraakan
	gender = GenderFemale

# Meta Crap
class GeneratorMeta:
	name = 'Draakan Species Package'
	description = 'Adds Draakan phsychological, physical and cultural data to the generator.'
	author = 'Liukcairo'
	copyright = 'Copyright (c) 2013 Robert MacGregor'
	license = 'GNU GPL version 3'

	""" Container class for data. """
	def custom_species(self):
		return [ SpeciesDraakan ]

	def custom_groups(self):
		return [ GroupElite ]

	def custom_locations(self):
		return [ LocationDrasLeona ]

	def custom_characters(self):
		return [ CharacterNyoka ]

class Modification:
	""" Main class object to load and initialize the Draakan plugin. """
	def __init__(self, **kwargs): return
	def get_commands(self): return { }
