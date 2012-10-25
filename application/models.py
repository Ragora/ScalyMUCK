"""
	models.py
	All models used in ScalyMUCK
	Copyright (c) 2012 Liukcairo
"""
import string

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

import hash
import database
import muckserver

Base = declarative_base()
# User Object
class User(Base):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	display_name = Column(String)
	description = Column(String)
	hash = Column(String)
	location_id = Column(Integer, ForeignKey('rooms.id'))
	
	inventory = relationship("Item")
	
	is_admin = Column(Integer)
	is_sadmin = Column(Integer)
	is_owner = Column(Integer)

	def __init__(self, name, description, password, location, inventory, admin, sadmin, owner):
		self.name = string.lower(name)
		self.display_name = name
		self.description = description
		self.hash = hash.generate_hash(password)
		self.location_id = location
		self.inventory = inventory
		self.is_admin = admin
		self.is_sadmin = sadmin
		self.is_owner = owner

	def __repr__(self):
		return "<User('%s','%s','%s','%u')>" % (self.name, self.description, self.hash, self.location)

# Item Object
class Item(Base):
	__tablename__ = 'items'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	display_name = Column(String)
	description = Column(String)
	owner_id = Column(Integer, ForeignKey('users.id'))
	location_id = Column(Integer, ForeignKey('rooms.id'))
	child = Column(Integer, ForeignKey('items.id'))

	def __init__(self, name, description, owner, location):
		self.name = string.lower(name)
		self.display_name = name
		self.description = description
		self.owner_id = owner
		self.location = location

	def __repr__(self):
		return "<Item('%s','%s','%u','%s')>" % (self.name, self.description, self.owner, self.location)
		
class Exit(Base):
	__tablename__ = 'exits'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	display_name = Column(String)
	code = Column(String)
	
	parent = Column(Integer, ForeignKey('rooms.id'))
	link = Column(Integer)
	
	def __init__(self, name, code, parent, link):
		self.name = string.lower(name)
		self.display_name = name
		self.code = code
		self.parent = parent
		self.link = link
		
	def __repr__(self):
		return "<Exit('%s','%s')>" % (self.name, self.code)

# Room Object
class Room(Base):
	__tablename__ = 'rooms'

	id = Column(Integer, primary_key=True)
	name = Column(String)
	display_name = Column(String)
	description = Column(String)
	owner_id = Column(Integer)

	users = relationship("User")
	exits = relationship("Exit")
	items = relationship("Item")
	parent = relationship("Item")

	def __init__(self, name, description, owner, users, exits, items):
		self.name = string.lower(name)
		self.display_name = name
		self.description = description
		self.owner = owner
		self.users = users
		self.exits = exits
		self.items = items

	def __repr__(self):
		return "<Room('%s','%s','%u'>" % (self.name, self.description, self.owner)

	def broadcast(self, message, exception=0):
		if (type(exception) is User):
			exception = exception.id
			
		session = database.new_session()
		user_contents = session.query(User).filter_by(location_id=self.id)
		for user_data in user_contents:
			connection = muckserver.find_connection(user_data.id)
			if (connection is not None and connection.id != exception):
				connection.send(message,0)

Base.metadata.create_all(database.engine())
database.init_database()
