"""
    manage_daemon.py
    Code used to spawn a Daemon of the server.
    Copyright (c) 2012 Liukcairo
"""

import sys

import server
import daemon

def main():
	print('ScalyMUCK Copyright (c) 2012 Liukcairo\n')
	
	if (sys.platform == 'win32'):
		print('Daemon mode is not available for Windows platforms.')
		return
	
	muck_server = server.Server('/tmp/scaly_muck.pid')
	muck_server.is_daemon = True
	
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			  print('Starting Daemon ...')
			  muck_server.start()
		elif 'stop' == sys.argv[1]:
			  print('Killing Daemon ...')
			  muck_server.stop()
		elif 'restart' == sys.argv[1]:
			  print('Restarting Daemon ...')
			  muck_server.restart()
		else:
			  print "Unknown command"
			  sys.exit(2)
		sys.exit(0)
	else:
		  print "Usage: %s [start|stop|restart]" % sys.argv[0]
		  sys.exit(2)
	return
      
if __name__ == '__main__':
	main()