"""
	database.py
	Quick database functions that should be used for read functions only.
	For writing to the database, use new_session() and control that session 
	as you need.
	Copyright (c) 2012 Liukcairo
"""
 
# There are no standard libraries to import

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

import models

global _alchemy_engine
_alchemy_engine = None

global _database_exists
_database_exists = True

def engine():
	global _alchemy_engine
	global _database_exists
	if (_alchemy_engine is None):
		try:
			with open('Data.db') as f: pass
		except IOError as e:
				_database_exists = False
		_alchemy_engine = create_engine('sqlite:///Data.db', echo=False)
	return _alchemy_engine
	
def new_session():
	global _alchemy_engine
	return scoped_session(sessionmaker(bind=_alchemy_engine))
	
def init_database():
	global _database_exists
	if (_database_exists == False):
		session = new_session()

		root_item = models.Item('Root','Root',0,0)
		session.add(root_item)
		
		root_user = models.User('RaptorJesus','Creator of all!',
								'ChangeThisPasswordNowPlox', 1, 
								[root_item], 1, 1, 1)
		session.add(root_user)
		
		portal_item = models.Item('Portal','The portal that everyone crosses through to enter this world.',0,1)
		session.add(portal_item)
		portal_room_exit = models.Exit('(East) to Engineering Room', 'east', 1, 2)
		session.add(portal_room_exit)
		engine_room_exit = models.Exit('(West) to Portal Room', 'west', 2, 1)
		session.add(engine_room_exit)
		
		portal_room = models.Room('Inter-Dimensional Portal', 'A portal that everyone crosses to enter into this world.', 
								  0, [root_user], [portal_room_exit], [portal_item])
		session.add(portal_room)
		
		engine_room = models.Room('Engineering Room','The room where all the portal systems are.', 0, [],[engine_room_exit],[] )
		session.add(engine_room)

		session.add(root_user)
		
		
		
		session.commit()
	return
		
def find_user_by_name(name):
	session = new_session()
	return session.query(models.User).filter_by(name=name).first()
	
def find_user_by_id(id):
	session = new_session()
	return session.query(models.User).get(id)
	
def find_item(id):
	session = new_session()
	return session.query(models.Item).get(id)
	
def find_room(id):
	session = new_session()
	return session.query(models.Room).get(id)
	
def find_users_in(id):
	session = new_session()
	return session.query(models.User).filter_by(location=id)
	
def find_items_in(id):
	session = new_session()
	return session.query(models.Item).filter_by(location=id)
	
def find_item_by_name_in(item_name, location_id):
	session = new_session()
	return session.query(models.Item).filter_by(location=location_id,name=item_name)
