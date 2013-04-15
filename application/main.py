"""
	main.py

	Main file for ScalyMUCK -- you just run this file!

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import sys
import os
import signal
import string
import logging
from time import strftime

from daemon import Daemon
from server import Server
from game import settings

class Application:
	""" Main application class. """
	server = None

	def sighandle(self, signum, frame):
		""" Used for asynchronous signal handling. """
		print(' ')
		print('Killing ScalyMUCK server...')
		self.server.shutdown()	
		logging.shutdown()

	def __init__(self, workdir, is_daemon=False):
		""" Called by main() or by the daemoniser code. """	
		workdir += '/'

		home_path = os.path.expanduser('~')
		data_path = home_path + '/.scalyMUCK/'

		config = settings.Settings(workdir + 'config/settings_server.cfg')
	
		# Prepare the logs
		# NOTE: This code looks sucky, could it be improved to look better?
		formatting = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s', '%d/%m/%y at %I:%M:%S %p')
		console_handle = logging.StreamHandler()
		if (config.get_index(index='LogConnections', datatype=bool)):
			logger = logging.getLogger('Connections')
			logger.setLevel(logging.INFO)

			file_handle = logging.FileHandler(data_path+'connection_log.txt')
			file_handle.setLevel(logging.DEBUG)
			file_handle.setFormatter(formatting)

			logger.info('ScalyMUCK Server Server Start')
			logger.addHandler(file_handle)
			if (is_daemon is False):
				logger.addHandler(console_handle)

		if (config.get_index(index='LogMods', datatype=bool)):
			logger = logging.getLogger('Mods')
			logger.setLevel(logging.INFO)

			file_handle = logging.FileHandler(data_path+'mod_log.txt')
			file_handle.setLevel(logging.INFO)
			file_handle.setFormatter(formatting)

			logger.info('ScalyMUCK Server Server Start')
			logger.addHandler(file_handle)
			if (is_daemon is False):
				logger.addHandler(console_handle)

		if (config.get_index(index='LogServer', datatype=bool)):
			logger = logging.getLogger('Server')
			logger.setLevel(logging.INFO)

			file_handle = logging.FileHandler(data_path+'server_log.txt')
			file_handle.setLevel(logging.INFO)
			file_handle.setFormatter(formatting)			

			logger.addHandler(file_handle)
			if (is_daemon is False):
				logger.addHandler(console_handle)
			logger.info('ScalyMUCK Server Server Start')

		self.server = Server(config=config, path=data_path, workdir=workdir)

		# Set the signals for asynchronous events
		signal.signal(signal.SIGINT, self.sighandle)
		signal.signal(signal.SIGTERM, self.sighandle)

		while (self.server.is_running):
			self.server.update()

		print(' ')
		print('Killing ScalyMUCK server ...')
		self.server.shutdown()	
		logging.shutdown()

class MUCKDaemon(Daemon):
	""" Used for daemonising the code. """

	def run(self, **kwargs):
		""" Called by the Daemonizer code. """
		Application(kwargs['workdir'], is_daemon=True)

def main():
	""" Called in the 'init' if below. """
	command = None
	if (len(sys.argv) == 2):
		command = string.lower(sys.argv[1])
		if (command != 'start' and command != 'stop' and command != 'restart'):
			print('Usage: ' + sys.argv[0] + ' <start|stop|restart>')
			return

	if (command is None):
		Application(os.getcwd())
	else:
		daemon = MUCKDaemon('/tmp/scaly_muck_pid.pid')
                if command == 'start':
                        daemon.start(workdir=os.getcwd())
                elif command == 'stop':
                        daemon.stop()
                elif command == 'restart':
                        daemon.restart()
                else:
                        print('Usage: ' + sys.argv[0] + ' <start|stop|restart>')
                        sys.exit(2)
                sys.exit(0)


if __name__ == '__main__':
	main()
