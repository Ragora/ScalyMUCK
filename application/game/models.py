"""
	models.py

	SQLAlchemy database models file
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

from blinker import signal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey
import bcrypt

import exception

Base = declarative_base()

""" Exits are what the players use to exit and move into other rooms in the ScalyMUCK
world. They may only have one target room ID which is used to assign .target to them
when they are loaded or creates by the game.World instance. """
class Exit(Base):
	__tablename__ = 'exits'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	target_id = Column(Integer, ForeignKey('rooms.id'))
	owner_id = Column(Integer, ForeignKey('players.id'))

	""" The Exit is not constructed manually by any of the modifications, this should be
	performed by calling the create_player function on the game.World instance provided
	to every modification. """
	def __init__(self, name, target_id=None, owner=0):
		self.name=name
		self.target_id = target_id
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	def __repr__(self):
		return "<Exit('%s','%u'>" % (self.name, self.target_id)

	""" This sets the name of the exit that is both displayed to the user and used to
	process user requests in regard to exit objects. The commit parameter is used if you don't
	want to dump changes to the database yet; if you're changing multiple properties at once, it
	doesn't hit the database as often then. """
	def set_name(self, name, commit=True):
		self.name = name
		if (commit is True):
			self.world.session.add(self)
			self.world.session.commit()
		
""" Players are well, the players that actually move and interact in the world. They
store their password hash and various other generic data that can be used across 
just about anything. """
class Player(Base):
	__tablename__ = 'players'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	display_name = Column(String)
	description = Column(String)
	hash = Column(String)
	work_factor = Column(Integer)
	
	location_id = Column(Integer, ForeignKey('rooms.id'))
	location = None
	inventory_id = Column(Integer)
	
	is_admin = Column(Boolean)
	is_sadmin = Column(Boolean)
	is_owner = Column(Boolean)

	connection = None
	world = None

	""" The Player is not constructed manually by any of the modifications, this should be
	performed by calling the create_player function on the game.World instance provided
	to every modification. """
	def __init__(self, name, password, work_factor, location_id, inventory_id, description='<Unset>', admin=False, sadmin=False, owner=False):
		self.name = string.lower(name)
		self.display_name = name
		self.description = description
		self.work_factor = work_factor
		self.location_id = location_id
		self.hash = bcrypt.hashpw(password, bcrypt.gensalt(work_factor))
		self.inventory_id = inventory_id
		self.is_admin = admin
		self.is_sadmin = sadmin
		self.is_owner = owner

	def __repr__(self):
		return "<User('%s','%s','%s','%u')>" % (self.name, self.description, self.hash, self.location_id)

	""" This sends a message to the relevant connection if there happens to be one established
	for this player object. If there is no active connection for this player, then the message
	is simply dropped. """
	def send(self, message):
		if (self.connection is not None):
			self.connection.send(message + '\n')
			return True
		else:
			return False

	""" This sets the location of the player object without any prior notification to the person
	being moved nor anyone in the original room or the target room. That is the calling modification's
	job to provide any relevant messages. """
	def set_location(self, location, commit=True):
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
		self.name = string.lower(name)
		self.display_name = name
		if (commit): self.commit()

	def set_password(self, password, commit=True):
		if (self.world is None):
			return

		self.hash = bcrypt.hashpw(password, bcrypt.gensalt(self.work_factor))
		if (commit): self.commit()

	""" This deletes the user from the game world and drops their connection if there 
	happens to be one established. As of now, the user's property will suddenly start
	pointing to a bad owner or perhaps even someone else if SQLAlchemy assigns someone
	their old ID. """
	def delete(self):
		self.disconnect()
		self.world.cached_players.remove(self)
		self.world.session.delete(self)
		self.world.session.commit()

	""" This drops the user's connection from the game, flushing any messages that
	were destined for them before actually booting them out of the server. This triggers
	the default disconnect message to be displayed by the ScalyMUCK core to whomever else
	may be in the room with the user at the time of their disconnect. """
	def disconnect(self):
		if (self.connection is not None):
			self.connection.socket_send()
			self.connection.deactivate()
			self.connection.sock.close()

	""" This sets the state as to whether or not the calling player instance is an administrator
	of the server or not. This may mean different things to different mods but -generally- it
	should just provide basic administrator privileges. The commit parameter is used if you don't
	want to dump changes to the database yet; if you're changing multiple properties at once, it
	doesn't hit the database as often then. """
	def set_is_admin(self, status, commit=True):
		self.is_admin = status
		if (self.is_sadmin is True and status is False):
			self.is_sadmin = False
		if (commit): self.commit()

	""" This sets the state as to whether or not the calling player instance is a super administrator
	of the server or not. This may mean different things to different mods but -generally- it
	should provide administrator functionalities more akin to what the owner may have, things that
	may break the server if used improperly. The commit parameter is used if you don't want to dump 
	changes to the database yet; if you're changing multiple properties at once, it doesn't hit the database as 
	often then. """
	def set_is_super_admin(self, status, commit=True):
		self.is_sadmin = status
		if (self.is_admin is False and status is True):
			self.is_admin = True
		if (commit): self.commit()

	def check_admin_trump(self, target):
		if (self.is_admin is True and target.is_admin is False):
			return True
		elif (self.is_sadmin is True and target.is_sadmin is False):
			return True
		elif (self.is_owner is True and target.is_owner is False):
			return True
		return False

	def commit(self):
		self.world.session.add(self)
		self.world.session.commit()

""" Bots are basically just the AI's of the game. They're not items, but they're not players
either. They have the special property of being interchangable with player object instances
for the most part except when it comes to certain functions -- such as having a password
hash. """
class Bot(Base):
	__tablename__ = 'bots'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	display_name = Column(String)
	location_id = Column(Integer, ForeignKey('rooms.id'))

	""" The Bot is not constructed manually by any of the modifications, this should be
	performed by calling the create_player function on the game.World instance provided
	to every modification. """
	def __init__(self):
		return

""" Items are really a generic object in ScalyMUCK, they're not players nor rooms nor exits but
serve multiple purposes. They can quite literally be an item, stored in the player's inventory
to be used later (like a potion) or they may be used to decorate rooms with specific objects
such as furniture or they may even be used to represent dead bodies. """	
class Item(Base):
	__tablename__ = 'items'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	owner = Column(Integer, ForeignKey('players.id'))
	description = Column(String)
	location_id = Column(Integer, ForeignKey('rooms.id'))

	""" The Item is not constructed manually by any of the modifications, this should be
	performed by calling the create_player function on the game.World instance provided
	to every modification. """
	def __init__(self, name, description, owner=0):
		self.name = name
		self.description = description
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	""" Produces a representation of the item, as to be expected. """
	def __repr__(self):
		return "<Item('%s','%s')>" % (self.name, self.description)

	def set_name(self, name, commit=True):
		""" Sets the name of the calling item of this function.

		Sets the name of this item that is both used in displaying to users and for processing
		relevant requests in regards to this item instance. 

		Keyword arguments:
			commit -- Determines whether or not this data should be commited immediately. It also includes other changes made
			by any previous function calls thay may have set this to false.

		"""

		self.name = name
		if (commit):
			self.world.session.add(self)
			self.world.session.commit()

	def set_location(self, location, commit=True):
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
	__tablename__ = 'rooms'
	id = Column(Integer, primary_key=True)

	name = Column(String)
	description = Column(String)
	items = relationship('Item')
	players = relationship('Player')
	bots = relationship('Bot')
	exits = relationship('Exit')
	owner_id = Column(Integer)

	""" The Room is not constructed manually by any of the modifications, this should be
	performed by calling the create_player function on the game.World instance provided
	to every modification.
	"""
	def __init__(self, name, description='<Unset>', owner=0):
		self.name = name
		self.description = description
		self.exits = [ ]
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	def __repr__(self):
		return "<Room('%s','%s')>" % (self.name, self.description)

	def add_exit(self, name, target_room, owner=0, commit=True):
		if (type(target_room) is int):
			target_room = self.world.session.query.query(Room).filter_by(id=target_room).first()
			if (target_room is not None):
				self.add_exit(name, target_room, commit=commit)
		elif (type(target_room) is Room):
			exit = Exit(name, target_room, owner)
			self.exits.append(exit)
			if (commit):
				self.world.session.add(self)
				self.world.session.add(exit)
				self.world.session.commit()

	def set_name(self, name, commit=True):
		self.name = name
		if (commit): self.commit()

	def broadcast(self, message, *exceptions):
		for player in self.players:
			if (player not in exceptions):
				player.send(message)

	def commit(self):
		self.world.session.add(self)
		self.world.session.commit()

	def find_player(self, id=None, name=None):
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		if (name is not None):
			name = string.lower(name)
			for player in self.players:
				if (name in player.name):
					return player
		elif (id is not None):
			return self.world.find_player(id=id)
		return None

	def find_item(self, id=None, name=None):
		if (id is None and name is None):
			raise exception.ModelArgumentError('No arguments specified (or were None)')

		if (name is not None):
			name = string.lower(name)
			for item in self.items:
				if (name in item.name):
					return item
		elif (id is not None):
			return self.world.find_item(id=id)
		return None
		
