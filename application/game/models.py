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
class Exit(Base):
	__tablename__ = 'exits'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	target_id = Column(Integer, ForeignKey('rooms.id'))
	owner_id = Column(Integer, ForeignKey('players.id'))

	def __init__(self, name, target_id, owner=0):
		self.name=name
		self.target_id = target_id
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	def __repr__(self):
		return "<Exit('%s','%u'>" % (self.name, self.target_id)

	def set_name(self, name):
		self.name = name
		self.world.session.add(self)
		self.world.session.commit()
		
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
	
	hp = Column(Integer)
	dexterity = Column(Integer)
	intelligence = Column(Integer)
	strength = Column(Integer)
	money = Column(Integer)

	is_admin = Column(Boolean)
	is_sadmin = Column(Boolean)
	is_owner = Column(Boolean)

	connection = None
	world = None

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

	def send(self, message):
		if (self.connection is not None):
			self.connection.send(message + '\n')
			return True
		else:
			return False

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

	def delete(self):
		self.disconnect()
		self.world.cached_players.remove(self)
		self.world.session.delete(self)
		self.world.session.commit()

	def disconnect(self):
		if (self.connection is not None):
			self.connection.socket_send()
			self.connection.deactivate()
			self.connection.sock.close()

	def set_is_admin(self, status, commit=True):
		self.is_admin = status
		if (self.is_sadmin is True and status is False):
			self.is_sadmin = False
		if (commit): self.commit()

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
	
class Item(Base):
	__tablename__ = 'items'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	owner = Column(Integer, ForeignKey('players.id'))
	description = Column(String)
	location_id = Column(Integer, ForeignKey('rooms.id'))

	def __init__(self, name, description, owner=0):
		self.name = name
		self.description = description
		if (type(owner) is int):
			self.owner_id = owner
		else:
			self.owner_id = owner.id

	def __repr__(self):
		return "<Item('%s','%s')>" % (self.name, self.description)

	def set_name(self, name, commit=True):
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
	exits = relationship('Exit')
	owner_id = Column(Integer)

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
		
