"""
	This is where all of ScalyMUCK's model definitions are located,
	save for the modifications that may extend the software in such
	a way that it demands for extra models but that is beyond the
	point. 

	The "base" definitions located in models.py are:
		* :class:`Exit`
		* :class:`Player`
		* :class:`Room`
		* :class:`Item`
		* :class:`Bot`

	All of the above classes inherit a few functions from :class:`ObjectBase` as well.

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

from blinker import signal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, String, Text, Boolean, MetaData, ForeignKey
import bcrypt

import exception

server = None
world = None
Base = declarative_base()

class ObjectBase:
	""" Base class used for the inheritance of useful member functions that work accross all models. """
	def delete(self):
		""" Deletes the object from the world. """
		self.session.delete(self)
		self.session.commit()

	def set_name(self, name, commit=True):
		""" Sets the name of the object.

		This sets the name of the object that is displayed and used to process requests towards it.

		Keyword arguments:
			* commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		self.name = name
		if (type(self) is Player):
			self.name = name.lower()
			self.display_name = name

		if (commit is True):
			self.session.add(self)
			self.session.commit()

	def set_location(self, location, commit=True):
		""" Sets the current location of this object.
	
		This sets the location of the object without any prior notification to the person
		being moved (if it's a player) nor anyone in the original room or the target room. 
		That is the calling modification's job to provide any relevant messages.

		Keyword arguments:
			* commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		if (type(self) is Room):
			return

		if (type(location) is Room):
			self.location = location
			self.location_id = location.id
			if (commit): self.commit()
		elif (type(location) is int):
			location = self.session.query(Room).filter_by(id=location).first()
			if (location is not None):
				self.set_location(location, commit=commit)

	def set_description(self, description, commit=True):
		""" Sets the description of this object.

		Sets the description of the calling object instance.

		Keyword arguments:
			* commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		self.description = description
		if (commit): self.commit()

	def commit(self):
		""" Commits any changes left in RAM to the database. """
		self.session.add(self)
		self.session.commit()

	def delete(self):
		""" Deletes the object from the world. If it is a :class:`Player` instance, the related
		connection is dropped from the server. """
		if (type(self) is Player):
			self.disconnect()

		self.session.delete(self)
		self.session.commit()

class Exit(Base, ObjectBase):
	""" 

	Exits are what the players use to exit and move into other rooms in the ScalyMUCK
	world. They may only have one target room ID which is used to assign .target to them
	when they are loaded or creates by the game.World instance. 

	"""

	__tablename__ = 'exits'

	id = Column(Integer, primary_key=True)
	""" This variable is the database number of the Exit. """
	name = Column(String(25))
	""" A short 25 character string that should be used for the name of the Exit. """
	description = Column(String(2000))
	""" A 2000 character string that is used to describe the Exit if it ever happens to be needed. """
	user_enter_message = Column(String(100))
	""" A 100 character string that represents the message displayed to the :class:`Player` using this exit. """
	room_enter_message = Column(String(100))
	""" A 100 character string that represents the message displayed to the user upon entering the target :class:`Room`. """
	user_exit_message = Column(String(100))
	""" A 100 character string that represents the message displayed to the :class:`Player` using this exit. """
	room_exit_message = Column(String(100))
	""" A 100 character string that is displayed to the inhabitants of the :class:`Room` this Exit is located in upon use. """
	target_id = Column(Integer)
	""" This variable is the database number of the :class:`Room` that this Exit points to. """
	location_id = Column(Integer, ForeignKey('rooms.id'))
	""" This variable is the database number of the :class:`Room` this Exit is in. """
	owner_id = Column(Integer, ForeignKey('players.id'))
	""" This variable is the database number of the :class:`Player` this Exit belongs to. """

	def __init__(self, name, target=None, owner=0):
		""" Initializes an instance of the Exit model.

		The Exit is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification.

		Keyword arguments:
			* target -- The ID or instance of a Room that this exit should be linking to.
			* owner -- The ID or instance of a Player that this should should belong to.

		"""
		if (target is None):
			raise exception.ModelArgumentError('No target was specified. (or it was None)')

		# Set the name
		self.name=name
		if (type(target) is int):
			self.target_id = target
		else:
			self.target_id = target.id

		# Set the owner
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

		self.user_enter_message = 'You move out.'
		self.room_enter_message = 'left.'
		self.user_exit_message = 'You arrive in the next room.'
		self.room_exit_message = 'arrived from another room.'
		self.description = '<Unset>'

	def __repr__(self):
		""" Produces a representation of the exit, as to be expected. """
		return "<Exit('%s','%u'>" % (self.name, self.target_id)
		
class Player(Base, ObjectBase):
	""" 

	Players are well, the players that actually move and interact in the world. They
	store their password hash and various other generic data that can be used across 
	just about anything. 

	"""
	__tablename__ = 'players'
	
	id = Column(Integer, primary_key=True)
	""" This variable is the database number of the Player. """
	name = Column(String(25))
	""" A short 25 character string representing the name of the Player. It should be all lower case. """
	display_name = Column(String(25))
	""" A short 25 character string representing the name of the Player that is displayed to other users. """
	description = Column(String(2000))
	""" A 2000 character string representing the description of the Player. """
	hash = Column(String(128))
	""" A 128 character string representing the password hash of the Player. """
	
	location_id = Column(Integer, ForeignKey('rooms.id'))
	""" This variable is the database id of the :class:`Room` this Player is located in. """
	location = None
	inventory_id = Column(Integer)
	""" This variable is the database id of the :class:`Room` that represents the Player's inventory. """
	
	is_admin = Column(Boolean)
	""" A boolean representing whether or not this Player is a server administrator. """
	is_sadmin = Column(Boolean)
	""" A boolean representing whether or not this Player is a server super administrator. """
	is_owner = Column(Boolean)
	""" A boolean representing whether or not this Player is a server owner. """

	connection = None
	world = None
	server = None
	interface = None

	def __init__(self, name=None, password=None, workfactor=None, location=None, inventory=None, description='<Unset>', admin=False, sadmin=False, owner=False):
		""" Initializes an instance of the Player model.

		The Player is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification. When the instance is created, it automatically generates a salt
		that the Player's password will be hashed with. This salt generation will cause a small
		lockup as the calculations are pretty intense depending on the work factor.

		Keyword arguments:
			* name -- The name of the Player that should be used.
			* password -- The password that should be used for this Player in the database.
			* workfactor -- The workfactor that should be used when generating this Player's hash salt.
			* location -- An ID or instance of Room that this Player should be created at.
			* inventory -- An ID or instance of Room that should represent this Player's inventory.
			* description -- A description that is shown when the player is looked at. Default: <Unset>
			* admin -- A boolean representing whether or not the player is an administrator or not. Default: False
			* sadmin -- A boolean representing whether or not the player is a super administrator or not. Default: False
			* owner -- A boolean representing whether or not the player is the owner of the server. Default: False
			
		"""
		self.name = string.lower(name)
		self.display_name = name
		self.description = description
		self.work_factor = workfactor

		if (type(location) is Room):
			location = location.id
		self.location_id = location
		if (type(inventory) is Room):
			inventory = inventory.id
		self.inventory_id = inventory

		self.hash = bcrypt.hashpw(password, bcrypt.gensalt(workfactor))
		self.is_admin = admin
		self.is_sadmin = sadmin
		self.is_owner = owner

	def __repr__(self):
		""" Produces a representation of the player, as to be expected. """
		return "<Player('%s','%s','%s','%u')>" % (self.name, self.description, self.hash, self.location_id)

	def send(self, message):
		""" Sends a message to this Player if they are connected.

		This sends a message to the relevant connection if there happens to be one established
		for this player object. If there is no active connection for this player, then the message
		is simply dropped.

		"""
		if (self.connection is None):
			self.connection = server.find_connection(self.id)

		if (self.connection is not None):
			self.connection.send(message + '\n')
			return True
		else:
			return False

	def set_password(self, password, commit=True):
		""" Sets the password of this Player.

		This sets the password of the Player in the database without any notification to the Player. This also
		triggers the new password to be hashed with a randomly generated salt which means the current thread
		of execution will probably hang for a few seconds unless the work factor is set just right.

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		self.hash = bcrypt.hashpw(password, bcrypt.gensalt(server.work_factor))
		if (commit is True): self.commit()

	def disconnect(self):
		""" Drops the Player's connection from the server.

		This drops the user's connection from the game, flushing any messages that
		were destined for them before actually booting them out of the server. This triggers
		the default disconnect message to be displayed by the ScalyMUCK core to whomever else
		may be in the room with the user at the time of their disconnect. 

		"""
		if (self.connection is not None):
			self.connection.socket_send()
			self.connection.deactivate()
			self.connection.sock.close()

	def set_is_admin(self, status, commit=True):
		""" Sets the administrator status of this Player.

		This sets the state as to whether or not the calling player instance is an administrator
		of the server or not. This may mean different things to different mods but -generally- it
		should just provide basic administrator privileges. The commit parameter is used if you don't
		want to dump changes to the database yet; if you're changing multiple properties at once, it
		doesn't hit the database as often then. 

		Keyword arguments:
			* commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		self.is_admin = status
		if (self.is_sadmin is True and status is False):
			self.is_sadmin = False
		if (commit): self.commit()

	def set_is_super_admin(self, status, commit=True):
		""" Sets the super administrator status of this Player.

		This sets the state as to whether or not the calling player instance is a super administrator
		of the server or not. This may mean different things to different mods but -generally- it
		should provide administrator functionalities more akin to what the owner may have, things that
		may break the server if used improperly. The commit parameter is used if you don't want to dump 
		changes to the database yet; if you're changing multiple properties at once, it doesn't hit the database as 
		often then. 

		Keyword arguments:
			* commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		self.is_sadmin = status
		if (self.is_admin is False and status is True):
			self.is_admin = True
		if (commit): self.commit()

	def check_admin_trump(self, target):
		""" Checks whether or not this Player trumps the target Player administratively.

		This returns True when the calling Player instance has greater privilege than that of the target they are being
		compared against. It returns false in the opposite situation.
		"""
		if (type(target) is not Player):
			raise exception.ModelArgumentError('Target is not an instance of Player!')

		if (self.is_admin is True and target.is_admin is False):
			return True
		elif (self.is_sadmin is True and target.is_sadmin is False):
			return True
		elif (self.is_owner is True and target.is_owner is False):
			return True
		else:
			return False

class Bot(Base, ObjectBase):
	"""

	Bots are basically just the AI's of the game. They're not items, but they're not players
	either. They have the special property of being interchangable with player object instances
	for the most part except when it comes to certain functions -- such as having a password
	hash. 

	"""
	__tablename__ = 'bots'

	id = Column(Integer, primary_key=True)
	""" This variable is the database number of the Bot. """
	name = Column(String(25))
	""" A short 25 character string representing the name of the Bot. It should be all lowercase. """
	description = Column(String(2000))
	""" A 2000 character string representing the description of the Bot. """
	display_name = Column(String(25))
	""" A 25 character string representing the name of the Bot displayed to Players. """
	location_id = Column(Integer, ForeignKey('rooms.id'))
	""" This variable is the database number of the :class:`Room` this Bot is located in. """

	def __init__(self, name=None, description=None, location=None):
		"""

		The Bot is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification. 

		"""
		self.name = name
		self.description = description
		self.display_name = name
		self.name = name.lower()

		if (type(location) is Room):
			location = location.id
		self.location_id = location

	def send(self, message):
		""" This is basically 'send' like for players except it does NOTHING. """

class Item(Base, ObjectBase):
	""" Base item model that ScalyMUCK uses.

	Items are really a generic object in ScalyMUCK, they're not players nor rooms nor exits but
	serve multiple purposes. They can quite literally be an item, stored in the player's inventory
	to be used later (like a potion) or they may be used to decorate rooms with specific objects
	such as furniture or they may even be used to represent dead bodies. 

	"""
	__tablename__ = 'items'
	
	id = Column(Integer, primary_key=True)
	""" This variable is the database number of this Item. """
	name = Column(String(25))
	""" A short 25 character string representing the name of the Item that is displayed to every connection
	related to a :class:`Player`. """
	owner_id = Column(Integer, ForeignKey('players.id'))
	""" This is the database number of the :class:`Player` that this Item belongs to. """
	description = Column(String(2000))
	""" A 2000 character string representing the description of this Item. """
	location_id = Column(Integer, ForeignKey('rooms.id'))
	""" This is the database number of the :class:`Room` that this Item is located in. """

	def __init__(self, name=None, description='<Unset>', owner=0):
		""" Constructor for the base item model.

		The Item is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification. 

		Keyword arguments:
			* name -- The name of the item that should be used.
			* description -- The description of the item that should be displayed. Default: <Unset>
			* owner -- Whoever should become the owner of this item, by instance or ID. Default: 0

		"""
		if (name is None):
			raise exception.ModelArgumentError('No name specified when attempting to create an instance of Item! (Or it is none)')

		self.name = name
		self.description = description
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	def __repr__(self):
		""" Produces a representation of the item, as to be expected. """
		return "<Item('%s','%s')>" % (self.name, self.description)

	def set_owner(self, owner):
		""" Sets a new owner for this item. """
		if (type(owner) is Player):
			owner = owner.id
		self.owner_id = owner
		self.commit()

class Room(Base, ObjectBase):
	""" Base room model that ScalyMUCK uses.

	Rooms are what make up the world inside of just about any MUCK really. Even if the rooms are not described as such, they still
	must be used to contain players, dropped items, bots, etc.

	"""
	__tablename__ = 'rooms'
	id = Column(Integer, primary_key=True)
	""" This is the database number of the Room. """

	name = Column(String(25))
	""" A short 25 character string representing the name of this Room that is displayed to every connection related to
	an instance of :class:`Player`. """
	description = Column(String(2000))
	""" A 2000 character string representing the description of this Room. """
	items = relationship('Item')
	""" An array that contains all instances of :class:`Item` contained in this Room. """
	players = relationship('Player')
	""" An array that contains all instances of :class:`Player` contained in this Room. """
	bots = relationship('Bot')
	""" An array that contains all instances of :class:`Bot` contained in this Room. """
	exits = relationship('Exit')
	""" An array that contains all instances of :class:`Exit` contained in this Room. """
	owner_id = Column(Integer)
	""" This is the database number of the :class:`Player` that this Room belongs to. """

	def __init__(self, name=None, description='<Unset>', owner=0):
		""" Initiates an instance of the Room model.

		The Room is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification.

		Keyword arguments:
			* name -- The name of the room that should be used.
			* description -- The description of the room.
			* owner -- The instance or ID of the relevant Player instance that should own this room.

		"""
		if (name is None):
			raise exception.ModelArgumentError('The name was not specified. (or it is None)')

		self.name = name
		self.description = description
		self.exits = [ ]
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	def __repr__(self):
		""" Produces a representation of the room, as to be expected. """
		return "<Room('%s','%s')>" % (self.name, self.description)

	def add_exit(self, name=None, target=None, owner=0):
		""" Gives this Room instance an Exit linking to anywhere.

		This produces an Exit link from the calling Room instance to another one elsewhere. The database
		changes are automatically committed here due to the way the exit has to be created in the database
		first for the changes to properly apply without any hackery to occur.

		Keyword arguments:
			* name -- The name of the exit that should be used.
			* target -- The ID or instance of a Room that this exit should be linking to.
			* owner -- The ID or instance of a Player that should become the owner of this Exit.

		"""
		if (name is None):
			raise exception.ModelArgumentError('The name was not specified. (or it was None)')
		elif (target is None):
			raise exception.ModelArgumentError('The target room was not specified. (or it was None)')

		if (type(target) is int):
			target = world.find_room(id=target)
			if (target is not None):
				self.add_exit(name, target)
		elif (type(target) is Room):
			exit = Exit(name, target, owner)
			self.exits.append(exit)
			self.session.add(self)
			self.session.add(exit)
			self.session.commit()

	def broadcast(self, message, *exceptions):
		""" Broadcasts a message to all inhabitants of the Room except those specified.

		This broadcasts a set message to all inhabitants of the Room except those specified after the message:
		some_room.broadcast('Dragons are best!', that_guy, this_guy, other_guy)

		The exceptions may be an ID or an instance.

		"""
		for player in self.players:
			if (player not in exceptions and player.id not in exceptions):
				player.send(message)

	def find_player(self, id=None, name=None):
		""" Locates a Player located in the calling instance of Room.
		
		This is a less computionally intensive version of the world's find_player as there is going to be much less data
		to be sorting through since you actually know where the Player is located (otherwise you wouldn't be calling this!)
		and all you need is the instance.

		Keyword arguments (one or the other):
			* id -- The identification number of the Player to locate inside of this room. This overrides the name if
			* both are specified.
			* name -- The name of the Player to locate.

		"""
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		player = None
		if (id is not None):
			for test_player in self.players:
				if (id == test_player.id):
					player = test_player
					break
		elif (name is not None):
			name = string.lower(name)
			for test_player in self.players:
				if (name in test_player.name.lower()):
					player = test_player
					break
		return player

	def find_bot(self, id=None, name=None):
		""" Locates a Bot located in the calling instance of Room.
		
		This is a less computionally intensive version of the world's find_bot as there is going to be much less data
		to be sorting through since you actually know where the Bot is located (otherwise you wouldn't be calling this!)
		and all you need is the instance.

		Keyword arguments (one or the other):
			* id -- The identification number of the Bot to locate inside of this room. This overrides the name if
			* both are specified.
			* name -- The name of the Bot to locate.

		"""
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		bot = None
		if (id is not None):
			for test_bot in self.bots:
				if (id == test_bot.id):
					bot = test_bot
					break
		elif (name is not None):
			name = string.lower(name)
			for test_bot in self.bots:
				if (name in test_bot.name.lower()):
					bot = test_bot
					break
		return bot

	def get_exits(self):
		""" Return a list of all exits. """
		for exit in self.exits:
			exit.location = self
		return self.exits

	def find_item(self, id=None, name=None):
		""" Locates an Item located in the calling instance of Room.
		
		This is a less computionally intensive version of the world's find_item as there is going to be much less data
		to be sorting through since you actually know where the Item is located (otherwise you wouldn't be calling this!)
		and all you need is the instance.

		Keyword arguments (one or the other):
			* id -- The identification number of the Item to locate inside of this room. This overrides the name if
			* both are specified.
			* name -- The name of the Item to locate.

		"""
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		item = None
		if (id is not None):
			for test_item in self.items:
				if (test_item.id == id):
					item = test_item
					break
		elif (name is not None):
			name = string.lower(name)
			for test_item in self.items:
				if (name in test_item.name.lower()):
					item = test_item
					break
		return item

	def find_exit(self, id=None, name=None):
		""" Locates an Item located in the calling instance of Room.
		
		This is a less computionally intensive version of the world's find_item as there is going to be much less data
		to be sorting through since you actually know where the Item is located (otherwise you wouldn't be calling this!)
		and all you need is the instance.

		Keyword arguments (one or the other):
			* id -- The identification number of the Item to locate inside of this room. This overrides the name if
			* both are specified.
			* name -- The name of the Item to locate.

		"""
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		exit = None
		if (id is not None):
			for test_exit in self.exits:
				if (test_exit.id == id):
					exit = test_exit
					break
		elif (name is not None):
			name = string.lower(name)
			for test_exit in self.exits:
				if (name in test_exit.name.lower()):
					exit = test_exit
					break
		return exit
