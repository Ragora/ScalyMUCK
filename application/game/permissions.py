"""
	permissions.py

	Permission handler for the ScalyMUCK server.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import logging

import settings

logger = logging.getLog('Mods')
class Permissions:
	""" Main class for permission handling in ScalyMUCK. """
	permissions = { }

	def set_permission(self, name, value, evaluator=None):
		""" Sets a permission in the repo. """
		if (evaluator is None):
			evaluator = self.standard_evaluator
		permissions[name] = (value, evaluator)

	def test_permission(self, name, player):
		""" Tests the permission availability against a player. """

	def standard_evaluator(self, name, player):
		""" Tests all standard permissions built into the server. """
		if (name == 'AllowAdminOverride'):
			return
		else:
			logger.warn('Attempted to evaluate undefined permission: "%s"!' % (name))
