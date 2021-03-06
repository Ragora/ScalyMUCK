"""
	ScalyMUCK has several base exceptions for the ScalyMUCK core and 
	ScalyMUCK modifications that may be loaded into the MUCK server.

	This software is licensed under the MIT license.
	Please refer to LICENSE.txt for more information.
"""

class ModApplicationError(Exception):
	""" Generic exception for ScalyMUCK modifications to subclass in order
	to report errors to the error reporting mechanism.

	NOTE:
		This should never be explictely raised by any code. This
		is designed to be subclassed for proper exception support.

	"""

class WorldArgumentError(ModApplicationError):
	""" Raised when using the world API and an invalid argument is specified. """

class ModelArgumentError(ModApplicationError):
	""" Raised when a model function is used improperly. """

class DatabaseError(ModApplicationError):
	""" Raised when an error occurs in the database. """
