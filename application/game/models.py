"""
	models.py

	SQLAlchemy database models file
	Copyright (c) 2013 Robert MacGregor

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

import string

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import bcrypt

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

	is_admin = Column(Integer)
	is_sadmin = Column(Integer)
	is_owner = Column(Integer)

	connection = None

	def __init__(self, name, password, work_factor, location_id, inventory_id, description='<Unset>', admin=0, sadmin=0, owner=0):
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

	def set_location(self, location):
		if (type(location) is Room):
			self.location = location
			self.location_id = location.id
			self.world.session.add(self)
			self.world.session.commit()
			return
		elif(type(location) is int):
			location = self.world.session.query(Room).filter_by(id=location).first()
			if (location is not None):
				self.set_location(location)
			return
		return

	def set_name(self, name):
		self.name = string.lower(name)
		self.display_name = name
		self.world.session.add(self)
		self.world.session.commit()

	def delete(self):
		if (self.connection is not None):
			self.connection.socket_send()
			self.connection.deactivate()
			self.connection.sock.close()
		self.world.cached_players.remove(self)
		self.world.session.delete(self)
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

	def set_name(self, name):
		self.name = name
		self.world.session.add(self)
		self.world.session.commit()

	def set_location(self, location):
		if (type(location) is Room):
			self.location = location
			self.location_id = location.id
			self.world.session.add(self)
			self.world.session.commit()
		elif(type(location) is int):
			location = self.world.session.query(Room).filter_by(id=location).first()
			if (location is not None):
				self.set_location(location)

		

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

	def add_exit(self, name, target_room, owner=0):
		if (type(target_room) is int):
			target_room = self.world.session.query.query(Room).filter_by(id=target_room).first()
			if (target_room is not None):
				self.add_exit(name, target_room)
			return
		elif (type(target_room) is Room):
			exit = Exit(name, target_room, owner)
			self.exits.append(exit)
			self.world.session.add(self)
			self.world.session.add(exit)
			self.world.session.commit()
			return
		return

	def set_name(self, name):
		self.name = name
		self.world.session.add(self)
		self.world.session.commit()

	def broadcast(self, message, *exceptions):
		for player in self.players:
			if (player not in exceptions):
				player.send(message)
		
