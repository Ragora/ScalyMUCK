"""
	telnet_host.py
	Copyright (c) 2012 The Liukcairo
	A small Telnet library I built.
"""

import socket, threading, time, string, sys

# There are no library imports
# There are no project specific library imports

class TelnetHost(threading.Thread):
	_id = 0
	_socket = 0
	_connections = [ ]
	_segment_length = 9
	_maximum_hosts = 10
	_text_buffer = ''
	_is_client = False
	_connected = False
	_address = 0
	_host = 0
	_port = 0
	_server = 0
	_should_terminate = False

	### --- Functions Begin
	"""
		TelnetHost.connect
		host: The remeote host to connect to.
		port: The port # to connect on.
		Description: Triggers this telnethost to connect to a remote
		host. Makes this host a client.
	"""
	def connect(self, host, port):
		self._is_client = True
		self._socket = socket.socket()
		self._host = host
		self._port = port
		self._socket.connect((self._host,int(self._port)))
		self.debugMessage('Attempting to connect to ' + self._host + ':' + str(self._port) + '...')
		recv = self._socket.recv(self._segment_length)
		# Then the connection was unsuccessful
		if (recv == ''):
			self.debug_message('Connection attempt to remote host ' + self._host + ':' + str(self._port) + ' failed!')
			self._socket.close()
			self._connected = False
			self.onConnectFailed()
			return

		# It's good!
		else:
			self.debugMessage('Connection to remote host ' + host + ':' + str(self._port) + ' successful!')
			self._server = 'Dummy'
			self._connected = True
			self.onConnected()
			self.onReceiveData(recv, 0)
			self.start()
		return

	"""
		TelnetHost.listen
		host: The IP to listen on.
		port: The port # to listen on.
		Description: Triggers this telnethost to listen on host:port. 
		Makes this host a client.
	"""
	def listen(self, host, port, maximum_hosts):
		self._maximum_hosts = maximum_hosts
		self._host = host
		self._port = port

		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		
		try:
			self._socket.bind((self._host,int(self._port)))
			self._socket.listen(int(self._maximum_hosts))
		except socket.error, e:
			return [ False, e]

		self._is_client = False
		self._connected = True

		# self.start()
		return [ True, 0 ]

	"""
		TelnetHost.shutdown
		Description: Forcefully shuts down the TelnetHost (terminates the thread), making
		it useless after. (As threads cannot be restarted.)
	"""
	def shutdown(self):
		self._connected = False
		if (self._is_client == False):
			self.broadCast('Server shutting down.\n')
			self.debugMessage('Server shutting down.')
			for connection in self._connections:
				connection.shutdown()
				connection._should_terminate = True
				del connection
		self._socket.close()
		self._should_terminate = True
		return
		
	"""
		TelnetHost.disconnect
		Description: Disconnects this TelnetHost from a remote server -or-
		if in server mode, shuts down the server.
	"""
	def disconnect(self):
		self._connected = False
		if (self._is_client == False):
			for connection in self._connections:
				connection.disconnect()
				del connection
		if (self._server != 'Dummy'):
			self._server._connections.remove(self)
		self._socket.close()
		return

	"""
		TelnetHost.Broadcast
		Msg: The message to send to all Connected hosts.
		Description: Sends a message to all Connected hosts if server. Otherwise,
		just sends Msg to the server we're Connected to.
	"""
	def broadCast(self, msg):
		if (self._is_client == True):
			self._socket.send(msg)
		else:
			for connection in self._connections:
				connection._socket.send(msg)
		return

	"""
		TelnetHost.send
		Msg: The message to send.
	"""
	def send(self, msg, host=0):
		if (self._connected == False):
			return
			
		if (self._is_client == True):
			self._socket.send(msg)
		else:
			if (host != ''):
				host.send(msg)
			else:
				for connection in self._connections:
					connection.send(msg)
		return

	### --- Callback functions
	"""
		TelnetHost.onConnected
		Description: This is called when the client successfully connects
		to a remote host.
	"""
	def onConnected(self):
		return

	"""
		TelnetHost.onClientConnected
		Host: The client that has Connected.
		Address: The address of the client that has
		Connected.
		Description: This is called when a client connects
		to the server.
	"""
	def onClientConnected(self, host):
		return

	"""
		TelnetHost.onClientDisconnect
		Host: The client that has disConnected.
		Description: This is called when a client disconnects from
		the server.
	"""
	def onClientDisconnect(self, host):
		del Host

	"""
		TelnetHost.onConnectFailed
		Description: This is called when the client is unable to connect
		to a remote host.
	"""
	def onConnectFailed(self):
		self.debugMessage('Failed to connect.')
		return

	"""
		TelnetHost.onReceiveData
		Data: The data we received.
		Host: If in server mode, this is the TelnetHost object that sent
		the message. It's simply 0 when we're in client mode.
		Description: This is called anytime we receive segmented data
		from the host.	
	"""
	def onReceiveData(self, data, host):
		sys.stdout.write(data)
		return
	
	"""
		TelnetHost.onReceiveLine
		Msg: The message we received.
		Host: If in server mode, this is the TelnetHost object that sent
		the message. When in client most, this is itself.
		Description: This is called when we processed a full line from the 
		host.
	"""
	def onReceiveLine(self, msg, host):
		return

	"""
		TelnetHost.debugMessage
		Msg: The message that the system sent back.
		Description: This function is called by TelnetHosts to relay information.
	"""
	def debugMessage(self, msg):
		return

	### --- Internal Functions. No Touchy!
	def run(self):
		while self._should_terminate is False:
			if (self._is_client == False):

				try:
					connection, address = self._socket.accept()
				except socket.error, e:
					sys.exit(0)
					return

				host = TelnetHost()
				host._socket = connection
				host._address = address
				host._connected = True
				host._server = self
				host._is_client = True
				host._id = len(self._connections)
				self._connections.append(host)
				host.start()
				self.debugMessage('Received client connection.')
				self.onClientConnected(host)
			else:
				try:
					recv = self._socket.recv(self._segment_length)
				except socket.error, e:
					self._server.debugMessage('Received client disconnect.')
					self.shutdown()
					self._server._connections.remove(self)
					self._server.onClientDisconnect(self)
					sys.exit(0)
					return
					
				### 
				if (recv == ''):
					if (self._server != 'Dummy'):
						self._server.debugMessage('Received client disconnect.')
						self.shutdown()
						self._server.onClientDisconnect(self)
						sys.exit(0)
						return
					
				
				### Since Recv is blocking, if we got here then we must have received some sort of message
				if (self._server != 'Dummy'):
					self._server.onReceiveData(recv, self)
				else:
					self.onReceiveData(recv, self)
					
				### Parse the incoming data from this connection
				if (string.find(recv, '\n') != -1):
					split = string.split(recv,'\n')
					if (self._server != 'Dummy'):
						self._server.onReceiveLine(self._text_buffer + split[0] + '\n', self)
					else:
						self.onReceiveLine(self._text_buffer + split[0] + '\n', self)
					self._text_buffer = ''

					for segment in split:
						if (segment == split[0]):
							continue
						else:
							self._text_buffer += segment
							if (string.find(segment, '\n') != -1):
								if (self._server != 'Dummy'):
									self._server.onReceiveLine(self._text_buffer, self)
								else:
									self.onReceiveLine(self._text_buffer, self)
								self._text_buffer = ''
				else:
					self._text_buffer += recv
				
		### Executed after the while loop above ends (happens on client/server shutdown)
		self.debugMessage('Server/client shutdown.')
		##self.shutdown()
		sys.exit(0)
		return

