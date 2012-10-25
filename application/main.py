"""
	main.py
    Main code for ScalyMUCK
	Copyright (c) 2012 Liukcairo
"""

import os, sys, time, signal

import sqlalchemy

import muckserver, models

# Intercept some signals
def onSignalReceived(signum, frame):
	print("Attempting to shutdown ScalyMUCK server...")
	global Running
	Running = False
	
# Erp.
signal.signal(signal.SIGINT, onSignalReceived)
signal.signal(signal.SIGTERM, onSignalReceived)
global Running
Running = True

"""
	Main function
"""
def main():
	# Check for any flags
	# print(sys.argv[1])
	server_connection = muckserver.connection
		
	### Attempt to listen on our configured address & Ports and return a status
	Success = server_connection.listen('0.0.0.0',23,32)
	if (Success[0] == False):
		print(Success[1])
		return
			
	global Running	
	### Start the Main Loop
	while Running:
		#print('loop')
		#time.sleep(1)
		server_connection.run()
	server_connection.shutdown()
	print('Shutdown complete.')
	sys.exit(0)

if __name__ == '__main__':
	main()
	
