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

import server
import settings

def main():
	command = None
	if (len(sys.argv) == 2):
		command = string.lower(sys.argv[1])
		if (command != 'start' and command != 'stop' and command != 'restart'):
			print('Usage: ' + sys.argv[0] + ' <start|stop|restart>')
			return
			

	# TODO: Make sure this code actually works on Windows as intended.
	home_path = os.path.expanduser('~')
	data_path = home_path + '/.scalyMUCK/'
	config = settings.Settings('config/settings_server.cfg')

	muck_server = server.Server(None, config, data_path)
	muck_server.is_daemon = False

	muck_server.initialise_server()
	while (muck_server.is_active()):
		muck_server.update()

if __name__ == '__main__':
	main()
