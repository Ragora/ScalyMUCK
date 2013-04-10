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

# NOTE: I hate using global but I need it so the async sighandle below can refer to the server object to perform a proper cleanup.
global server
server = None

def sighandle(signum, frame):
	""" Used for asynchronous signal handling. """
	print(' ')
	print('Killing ScalyMUCK server...')
	server.shutdown()	
	logging.shutdown()

def server_main(workdir):
	""" Called by main() or by the daemoniser code. """	
	workdir += '/'

	home_path = os.path.expanduser('~')
	data_path = home_path + '/.scalyMUCK/'

	config = settings.Settings(workdir + 'config/settings_server.cfg')
	
	# Prepare the logs
	# NOTE: This code looks sucky, could it be improved to look better?
	formatting = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s', '%d/%m/%y at %I:%M:%S %p')
	if (config.get_index(index='LogConnections', datatype=bool)):
		logger = logging.getLogger('Connections')
		logger.setLevel(logging.INFO)

		handle = logging.FileHandler(data_path+'connection_log.txt')
		handle.setLevel(logging.DEBUG)

		handle.setFormatter(formatting)
		logger.addHandler(handle)
		logger.info('ScalyMUCK Server Server Start')

	if (config.get_index(index='LogMods', datatype=bool)):
		logger = logging.getLogger('Mods')
		logger.setLevel(logging.INFO)

		handle = logging.FileHandler(data_path+'mod_log.txt')
		handle.setLevel(logging.INFO)
		handle.setFormatter(formatting)

		logger.addHandler(handle)
		logger.info('ScalyMUCK Server Server Start')

	if (config.get_index(index='LogServer', datatype=bool)):
		logger = logging.getLogger('Server')
		logger.setLevel(logging.INFO)

		handle = logging.FileHandler(data_path+'server_log.txt')
		handle.setLevel(logging.INFO)
		handle.setFormatter(formatting)

		logger.addHandler(handle)
		logger.info('ScalyMUCK Server Server Start')

	global server
	server = Server(config=config, path=data_path, workdir=workdir)

	# Set the signals for asynchronous events
	signal.signal(signal.SIGINT, sighandle)
	signal.signal(signal.SIGTERM, sighandle)

	while (server.is_running):
		server.update()

	print(' ')
	print('Killing ScalyMUCK server ...')
	server.shutdown()	
	logging.shutdown()

class MUCKDaemon(Daemon):
	""" Used for daemonising the code. """

	def run(self, **kwargs):
		""" Called by the Daemonizer code. """
		server_main(kwargs['workdir'])
		return

def main():
	""" Called in the 'init' if below. """
	command = None
	if (len(sys.argv) == 2):
		command = string.lower(sys.argv[1])
		if (command != 'start' and command != 'stop' and command != 'restart'):
			print('Usage: ' + sys.argv[0] + ' <start|stop|restart>')
			return

	if (command is None):
		server_main(os.getcwd())
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
