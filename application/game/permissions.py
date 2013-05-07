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

logger = logging.getLogger('Mods')
class Permissions:
	""" Main class for permission handling in ScalyMUCK. """
	permissions = { }
	workdir = None

	def __init__(self, workdir=None):
		self.workdir = workdir
		permission_settings = settings.Settings('%s/config/permissions.cfg' % (self.workdir))
		for index in permission_settings.get_indices():
			self.set_permission(index, permission_settings.get_index(index, bool))

	def set_permission(self, name=None, value=None, evaluator=None):
		""" Sets a permission in the repo. """
		if (evaluator is None):
			evaluator = self.standard_evaluator
		self.permissions[name] = (value, evaluator)

	def has_permission(self, name):
		""" Determines whether or not a permission is actually set in the repo. """
		if (name in self.permissions):
			return True
		else:
			return False

	def test(self, name=None, player=None):
		""" Tests the permission availability against a player. """
		if (name in self.permissions):
			value, evaluator = self.permissions[name]
			return evaluator(name, player, value)

	def standard_evaluator(self, name=None, player=None, value=None):
		""" Tests all standard permissions built into the server. """
		if (name == 'AllowAdminOverride'):
			return value
		elif (name == 'AllowSuperAdminOverride'):
			return value
		elif (name == 'AllowOwnerOverride'):
			return value
		else:
			logger.warn('Attempted to evaluate undefined permission: "%s"!' % (name))
			return False
