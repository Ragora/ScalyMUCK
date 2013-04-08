"""
	models.py

	This is where all of ScalyMUCK's model definitions are located,
	save for the modifications that may extend the software in such
	a way that it demands for extra models but that is beyond the
	point. 

	The "base" definitions located here are:
		Exit
		Player
		Room
		Item
		Bot

	Copyright (c) 2013 Robert MacGregor
	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

from blinker import signal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, Text, Boolean, MetaData, ForeignKey
import bcrypt

import exception

Base = declarative_base()

class Exit(Base):
	""" 

	Exits are what the players use to exit and move into other rooms in the ScalyMUCK
	world. They may only have one target room ID which is used to assign .target to them
	when they are loaded or creates by the game.World instance. 

	"""
	__tablename__ = 'exits'

	id = Column(Integer, primary_key=True)
	name = Column(Text)
	target_id = Column(Integer, ForeignKey('rooms.id'))
	owner_id = Column(Integer, ForeignKey('players.id'))

	def __init__(self, name, target=None, owner=0):
		""" Initializes an instance of the Exit model.

		The Exit is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification.

		Keyword arguments:
			target -- The ID or instance of a Room that this exit should be linking to.
			owner -- The ID or instance of a Player that this should should belong to.

		"""
		if (target is None):
			raise exception.ModelArgumentError('No target was specified. (or it was None)')

		self.name=name
		if (type(target) is int):
			self.target_id = target
		else:
			self.target_id = target.id

		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	def __repr__(self):
		""" Produces a representation of the exit, as to be expected. """
		return "<Exit('%s','%u'>" % (self.name, self.target_id)

	def set_name(self, name, commit=True):
		""" Sets the name of the exit.

		This sets the name of the exit that is both displayed to the user and used to process user 
		requests in regard to exit objects. The commit parameter is used if you don't want to dump 
		changes to the database yet; if you're changing multiple properties at once, it doesn't hit 
		the database needlessly as often then.

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		self.name = name
		if (commit is True):
			self.world.session.add(self)
			self.world.session.commit()
		
class Player(Base):
	""" 

	Players are well, the players that actually move and interact in the world. They
	store their password hash and various other generic data that can be used across 
	just about anything. 

	"""
	__tablename__ = 'players'
	
	id = Column(Integer, primary_key=True)
	name = Column(Text)
	display_name = Column(Text)
	description = Column(Text)
	hash = Column(Text)
	work_factor = Column(Integer)
	
	location_id = Column(Integer, ForeignKey('rooms.id'))
	location = None
	inventory_id = Column(Integer)
	
	is_admin = Column(Boolean)
	is_sadmin = Column(Boolean)
	is_owner = Column(Boolean)

	connection = None
	world = None

	def __init__(self, name=None, password=None, workfactor=None, location=None, inventory=None, description='<Unset>', admin=False, sadmin=False, owner=False):
		""" Initializes an instance of the Player model.

		The Player is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification. When the instance is created, it automatically generates a salt
		that the Player's password will be hashed with. This salt generation will cause a small
		lockup as the calculations are pretty intense depending on the work factor.

		Keyword arguments:
			name -- The name of the Player that should be used.
			password -- The password that should be used for this Player in the database.
			workfactor -- The workfactor that should be used when generating this Player's hash salt.
			location -- An ID or instance of Room that this Player should be created at.
			inventory -- An ID or instance of Room that should represent this Player's inventory.
			description -- A description that is shown when the player is looked at. Default: <Unset>
			admin -- A boolean representing whether or not the player is an administrator or not. Default: False
			sadmin -- A boolean representing whether or not the player is a super administrator or not. Default: False
			owner -- A boolean representing whether or not the player is the owner of the server. Default: False
			
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
		if (self.connection is not None):
			self.connection.send(message + '\n')
			return True
		else:
			return False

	def set_location(self, location, commit=True):
		""" Sets the current location of this Player.
	
		This sets the location of the player object without any prior notification to the person
		being moved nor anyone in the original room or the target room. That is the calling modification's
		job to provide any relevant messages.

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		if (type(location) is Room):
			self.location = location
			self.location_id = location.id
			if (commit): self.commit()
			return
		elif (type(location) is int):
			location = self.world.session.query(Room).filter_by(id=location).first()
			if (location is not None):
				self.set_location(location, commit=commit)
			return
		return

	def set_name(self, name, commit=True):
		""" Sets the name of this Player.

		This sets of the name of the Player in the database without any notification to either the Player
		or anyone in the room with the Player.

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		self.name = string.lower(name)
		self.display_name = name
		if (commit): self.commit()

	def set_password(self, password, commit=True):
		""" Sets the password of this Player.

		This sets the password of the Player in the database without any notification to the Player. This also
		triggers the new password to be hashed with a randomly generated salt which means the current thread
		of execution will probably hang for a few seconds unless the work factor is set just right.

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		if (self.world is None):
			return

		self.hash = bcrypt.hashpw(password, bcrypt.gensalt(self.work_factor))
		if (commit): self.commit()

	def delete(self):
		""" Deletes the Player from the world and terminates their connection.

		This deletes the Player from the game world and drops their connection if there 
		happens to be one established. As of now, the user's property will suddenly start
		pointing to a bad owner or perhaps even someone else if SQLAlchemy assigns someone
		their old ID. The changes are automatically committed once this action is performed.

		"""
		self.disconnect()
		self.world.cached_players.remove(self)
		self.world.session.delete(self)
		self.world.session.commit()

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
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
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
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
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

	def commit(self):
		""" Commits any changes left in RAM to the database. """
		self.world.session.add(self)
		self.world.session.commit()

class Bot(Base):
	"""

	Bots are basically just the AI's of the game. They're not items, but they're not players
	either. They have the special property of being interchangable with player object instances
	for the most part except when it comes to certain functions -- such as having a password
	hash. 

	"""

	__tablename__ = 'bots'

	id = Column(Integer, primary_key=True)
	name = Column(Text)
	display_name = Column(Text)
	location_id = Column(Integer, ForeignKey('rooms.id'))

	def __init__(self):
		"""

		The Bot is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification. 

		"""

		return

class Item(Base):
	""" Base item model that ScalyMUCK uses.

	Items are really a generic object in ScalyMUCK, they're not players nor rooms nor exits but
	serve multiple purposes. They can quite literally be an item, stored in the player's inventory
	to be used later (like a potion) or they may be used to decorate rooms with specific objects
	such as furniture or they may even be used to represent dead bodies. 

	"""
	__tablename__ = 'items'
	
	id = Column(Integer, primary_key=True)
	name = Column(Text)
	owner_id = Column(Integer, ForeignKey('players.id'))
	description = Column(Text)
	location_id = Column(Integer, ForeignKey('rooms.id'))

	def __init__(self, name=None, description='<Unset>', owner=0):
		""" Constructor for the base item model.

		The Item is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification. 

		Keyword arguments:
			name -- The name of the item that should be used.
			description -- The description of the item that should be displayed. Default: <Unset>
			owner -- Whoever should become the owner of this item, by instance or ID. Default: 0

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

	def set_name(self, name, commit=True):
		""" Sets the name of the calling item of this function.

		Sets the name of this item that is both used in displaying to users and for processing
		relevant requests in regards to this item instance. 

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""

		self.name = name
		if (commit):
			self.world.session.add(self)
			self.world.session.commit()

	def set_location(self, location, commit=True):
		""" Sets the location of the calling item of this function.

		Sets the location of the calling item in database unless the commit keyword argument 
		is set to be False.

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True

		"""
		if (type(location) is Room):
			self.location = location
			self.location_id = location.id
			if (commit):
				self.world.session.add(self)
				self.world.session.commit()
		elif (type(location) is int):
			location = self.world.session.query(Room).filter_by(id=location).first()
			if (location is not None):
				self.set_location(location, commit=commit)

class Room(Base):
	""" Base room model that ScalyMUCK uses.

	Rooms are what make up the world inside of just about any MUCK really. Even if the rooms are not described as such, they still
	must be used to contain players, dropped items, bots, etc.

	"""
	__tablename__ = 'rooms'
	id = Column(Integer, primary_key=True)

	name = Column(Text)
	description = Column(Text)
	items = relationship('Item')
	players = relationship('Player')
	bots = relationship('Bot')
	exits = relationship('Exit')
	owner_id = Column(Integer)

	def __init__(self, name=None, description='<Unset>', owner=0):
		""" Initiates an instance of the Room model.

		The Room is not constructed manually by any of the modifications, this should be
		performed by calling the create_player function on the game.World instance provided
		to every modification.

		Keyword arguments:
			name -- The name of the room that should be used.
			description -- The description of the room.
			owner -- The instance or ID of the relevant Player instance that should own this room.

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
			name -- The name of the exit that should be used.
			target -- The ID or instance of a Room that this exit should be linking to.
			owner -- The ID or instance of a Player that should become the owner of this Exit.
		"""
		if (name is None):
			raise exception.ModelArgumentError('The name was not specified. (or it was None)')
		elif (target_room is None):
			raise exception.ModelArgumentError('The target room was not specified. (or it was None)')

		if (type(target) is int):
			target = self.world.find_room(id=target)
			if (target is not None):
				self.add_exit(name, target)
		elif (type(target) is Room):
			exit = Exit(name, target, owner)
			self.exits.append(exit)
			self.world.session.add(self)
			self.world.session.add(exit)
			self.world.session.commit()

	def set_name(self, name, commit=True):
		""" Sets the name of this Room.

		Sets the name of the calling Room instance.

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false. Default: True
		"""
		self.name = name
		if (commit): self.commit()

	def broadcast(self, message, *exceptions):
		""" Broadcasts a message to all inhabitants of the Room except those specified.

		This broadcasts a set message to all inhabitants of the Room except those specified after the message:
		some_room.broadcast('Dragons are best!', that_guy, this_guy, other_guy)

		The exceptions may be an ID or an instance.
		"""
		for player in self.players:
			if (player not in exceptions and player.id not in exceptions):
				player.send(message)

	def commit(self):
		""" Commits any changes left in RAM to the database."""
		self.world.session.add(self)
		self.world.session.commit()

	def find_player(self, id=None, name=None):
		""" Locates a Player located in the calling instance of Room.
		
		This is a less computionally intensive version of the world's find_player as there is going to be much less data
		to be sorting through since you actually know where the Player is located (otherwise you wouldn't be calling this!)
		and all you need is the instance.

		Keyword arguments (one or the other):
			id -- The identification number of the Player to locate inside of this room. This overrides the name if
			both are specified.
			name -- The name of the Player to locate.
		"""
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		if (id is not None):
			return self.world.find_player(id=id)
		elif (name is not None):
			name = string.lower(name)
			for player in self.players:
				if (name in player.name):
					return player
		else:
			return None

	def find_item(self, id=None, name=None):
		""" Locates an Item located in the calling instance of Room.
		
		This is a less computionally intensive version of the world's find_item as there is going to be much less data
		to be sorting through since you actually know where the Item is located (otherwise you wouldn't be calling this!)
		and all you need is the instance.

		Keyword arguments (one or the other):
			id -- The identification number of the Item to locate inside of this room. This overrides the name if
			both are specified.
			name -- The name of the Item to locate.
		"""
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		if (id is not None):
			return self.world.find_item(id=id)
		elif (name is not None):
			name = string.lower(name)
			for item in self.items:
				if (name in item.name):
					return item
		else:
			return None
		
