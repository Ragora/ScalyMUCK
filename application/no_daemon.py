"""
	main.py
	Main file for ScalyMUCK -- you just run this file!
	Copyright (c) 2012 Liukcairo
"""

import sys

import server
import settings

def main():
	print('ScalyMUCK Copyright (c) 2012 Liukcairo')
	print('ScalyMUCK no daemon mode.\n')
	
	muck_server = server.Server('')
	muck_server.is_daemon = False
	
	muck_server.initialise_server()
	while (muck_server.is_active()):
		muck_server.update()

if __name__ == '__main__':
	main()