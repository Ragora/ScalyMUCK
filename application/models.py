"""
    models.py
    SQLAlchemy database models file
    Copyright (c) 2012 Liukcairo
"""

import string

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import bcrypt

Base = declarative_base()
class Player(Base):
	__tablename__ = 'players'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	display_name = Column(String)
	description = Column(String)
	hash = Column(String)
	work_factor = Column(Integer)
	location = Column(Integer, ForeignKey('rooms.id'))
	inventory = Column(Integer, ForeignKey('rooms.id'))
	
	hp = Column(Integer)
	dexterity = Column(Integer)
	intelligence = Column(Integer)
	strength = Column(Integer)

	is_admin = Column(Integer)
	is_sadmin = Column(Integer)
	is_owner = Column(Integer)

	def __init__(self, name, password, work_factor, location, inventory, description='<Unset>', admin=0, sadmin=0, owner=0):
		self.name = string.lower(name)
		self.display_name = name
		self.description = description
		self.work_factor = work_factor
		self.hash = bcrypt.hashpw(password, bcrypt.gensalt(work_factor))
		self.inventory = inventory
		self.is_admin = admin
		self.is_sadmin = sadmin
		self.is_owner = owner

	def __repr__(self):
		return "<User('%s','%s','%s','%u')>" % (self.name, self.description, self.hash, self.location)
	      
class Room(Base):
	__tablename__ = 'rooms'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)

	def __init__(self, name, description='<Unset>'):
		self.name = name
		self.description = description

	def __repr__(self):
		return "<Room('%s','%s')>" % (self.name, self.description)
	      
class Item(Base):
	__tablename__ = 'items'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	location = Column(Integer, ForeignKey('rooms.id'))
	inventory = Column(Integer, ForeignKey('rooms.id'))

	def __init__(self, name, description):
		self.name = string.lower(name)
		self.description = description

	def __repr__(self):
		return "<Item('%s','%s')>" % (self.name, self.description)
