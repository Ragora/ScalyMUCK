"""
	muck.py

	Main file for ScalyMUCK -- you just run this file!
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import sys
import os
import string
import logging
from time import strftime

from server import Server
from game import settings

def main():
	command = None
	if (len(sys.argv) == 2):
		command = string.lower(sys.argv[1])
		if (command != 'start' and command != 'stop' and command != 'restart'):
			print('Usage: ' + sys.argv[0] + ' <start|stop|restart>')
			return
			
	home_path = os.path.expanduser('~')
	data_path = home_path + '/.scalyMUCK/'

	config = settings.Settings('config/settings_server.cfg')
	
	# Prepare the logs
	formatting = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s', '%d/%m/%y at %I:%M:%S %p')
	if (config.get_index('LogConnections', bool)):
		logger = logging.getLogger('Connections')
		logger.setLevel(logging.INFO)

		handle = logging.FileHandler(data_path+'connection_log.txt')
		handle.setLevel(logging.DEBUG)

		handle.setFormatter(formatting)
		logger.addHandler(handle)
		logger.info('ScalyMUCK Server Server Start')

	if (config.get_index('LogMods', bool)):
		logger = logging.getLogger('Mods')
		logger.setLevel(logging.INFO)

		handle = logging.FileHandler(data_path+'mod_log.txt')
		handle.setLevel(logging.INFO)
		handle.setFormatter(formatting)

		logger.addHandler(handle)
		logger.info('ScalyMUCK Server Server Start')

	if (config.get_index('LogServer', bool)):
		logger = logging.getLogger('Server')
		logger.setLevel(logging.INFO)

		handle = logging.FileHandler(data_path+'server_log.txt')
		handle.setLevel(logging.INFO)
		handle.setFormatter(formatting)

		logger.addHandler(handle)
		logger.info('ScalyMUCK Server Server Start')

	muck_server = Server(None, config, data_path)
	muck_server.is_daemon = False

	# TODO: Can probably write to be a tad better
	while (muck_server.is_active()):
		try:
			muck_server.update()
		except KeyboardInterrupt as e:
			print(' ')
			print('Killing ScalyMUCK server ...')
			muck_server.shutdown()
			
	logging.shutdown()

if __name__ == '__main__':
	main()
