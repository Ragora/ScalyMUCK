"""
	Exceptions for ScalyMUCK core and ScalyMUCK modifications that
	may be loaded into the MUCK server.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

class ModApplicationError(Exception):
	""" Generic """

class WorldArgumentError(ModApplicationError):
	""" Raised when using the world API and an invalid
	argument is specified. 

	"""

class ModelArgumentError(ModApplicationError):
	""" Raised when a model function is used improperly.
	"""
