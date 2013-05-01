"""
	permissions.py

	Permission handler for the ScalyMUCK server.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import settings

class Permissions:
	""" Main class for permission handling in ScalyMUCK. """
	permissions = { }

	def set_permission(self, name, value):
		""" Sets a permission in the repo. """
		permissions[name] = value

	def test_permission(self, name, player):
		""" Tests the permission availability against a player. """
