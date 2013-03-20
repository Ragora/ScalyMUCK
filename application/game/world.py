"""
	world.py

	Game world code for ScalyMUCK
	Copyright (c) 2013 Robert MacGregor

	TODO: Organize this code perhaps? Ugh...

	This software is licensed under the GNU General
	Public License version 3. Please refer to gpl.txt 
	for more information.
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from models import Room, Player, Item

class World():
	engine = None
	session = None
	
	cached_players = [ ]
	cached_items = [ ]
	cached_rooms = [ ]
	cached_exits = [ ]
	def __init__(self, engine):
		self.engine = engine
		self.session = scoped_session(sessionmaker(bind=self.engine))
		return
	      
	def create_room(self, name, description='<Unset>', owner=0):
		room = Room(name, description, owner)
		room.world = self
		self.session.add(room)
		self.session.commit()

		self.cached_rooms.append(room)
		return room
	      
	def find_room(self, id=None, name=None):
		if (name is None and id is None):
			return None

		for room in self.cached_rooms:
			if (room.id == id or room.name == name):
				return room

		if (name is not None):
			target_room = self.session.query.query(Room).filter_by(name=name).first()
			if (target_room is not None):
				target_room.world = self
				self.cached_rooms.append(target_room)
				
				for item in target_room.items:
					if (self.item_loaded(item.id) is False):
						self.cached_items.append(item)
				for player in target_room.players:
					if (self.player_loaded(player.id) is False):
						self.cached_players.append(player)
				for exit in target_room.exits:
					if (self.exit_loaded(exit.id) is False):
						self.cached_exits.append(exit)
				return target_room 
		else:
			target_room = self.session.query(Room).filter_by(id=id).first()
			if (target_room is not None):
				target_room.world = self
				self.cached_rooms.append(target_room)

				for item in target_room.items:
					if (self.item_loaded(item.id) is False):
						self.cached_items.append(item)
				for player in target_room.players:
					if (self.player_loaded(player.id) is False):
						self.cached_players.append(player)
				for exit in target_room.exits:
					if (self.exit_loaded(exit.id) is False):
						self.cached_exits.append(exit)
				return target_room
		return None
	
	def create_player(self, name, password, work_factor, location):
		player_inventory = self.create_room(name + "'s Inventory")	
			
		player = Player(name, password, work_factor, location.id, 0)
		player.world = self
		player.inventory_id = player_inventory.id
		self.session.add(player)

		location.players.append(player)
		self.session.add(location)

		self.session.add(player_inventory)
		self.session.commit()
		
		player.location = location
		player.inventory = player_inventory
		self.cached_players.append(player)
		self.cached_rooms.append(player_inventory)
		return player
	      
	def find_player(self,id=None,name=None,display_name=None):
		if (name is None and id is None):
			return None

		for player in self.cached_players:
			if (player.id == id or player.name == name or player.display_name == display_name):
				return player
				 
		if (name is not None):
			target_player = self.session.query(Player).filter_by(name=name).first()
			if (target_player is not None):
				target_player.world = self
				self.cached_players.append(target_player)
				if (self.room_loaded(target_player.location_id) is False):
					target_player.location = self.session.query(Room).filter_by(id=target_player.location_id).first()
					self.cached_rooms.append(target_player.location)
				else:
					target_player.location = self.find_room(id=target_player.location_id)

				if (self.room_loaded(target_player.inventory_id) is False):
					target_player.inventory = self.session.query(Room).filter_by(id=target_player.inventory_id).first()
					self.cached_rooms.append(target_player.inventory)
				else:
					target_player.inventory = self.find_room(id=target_player.inventory_id)
				return target_player
		else:
			target_player = self.session.query(Player).filter_by(id=id).first()
			if (target_player is not None):
				target_player.world = self
				self.cached_players.append(target_player)
				if (self.room_loaded(target_player.location_id) is False):
					target_player.location = self.session.query(Room).filter_by(id=target_player.location_id).first()
					self.cached_rooms.append(target_player.location)
				else:
					target_player.location = self.find_room(id=target_player.location_id)

				if (self.room_loaded(target_player.inventory_id) is False):
					target_player.inventory = self.session.query(Room).filter_by(id=target_player.inventory_id).first()
					self.cached_rooms.append(target_player.inventory)
				else:
					target_player.inventory = self.find_room(id=target_player.inventory_id)
				return target_player
		return None

	def get_players(self):
		list = [ ]
		self.session.query(Player).filter_by()
		for player in self.session.query(Player).filter_by():
			list.append(self.find_player(id=player.id))
		return list

	def find_item(self, id):
		if (id is None):
			return None

		for item in self.cached_items:
			if (item.id == id):
				return item

		target_item = self.session.query(Item).filter_by(id=id).first()
		if (target_item is not None):
			target_item.location = self.session.query(Room).filter_by(id=target_item.location_id).first()
			target_item.world = self
			return target_item

	def create_item(self, name, description, owner, location):
		item = Item(name, description, owner)
		if (type(location) is int):
			item.location_id = location
			item.location = self.session.query(Room).filter_by(id=location).first()
		else:
			item.location = location
			item.location_id = location.id

		item.world = self
		self.session.add(item)
		self.session.commit()

		self.cached_items.append(item)
		return item

	def item_loaded(self, id):
		for item in self.cached_items:
			if (item.id == id):
				return True
		return False

	def player_loaded(self, id):
		for player in self.cached_players:
			if (player.id == id):
				return True
		return False

	def room_loaded(self, id):
		for room in self.cached_rooms:
			if (room.id == id):
				return True
		return False

	def exit_loaded(self, id):
		for exit in self.cached_exits:
			if (exit.id == id):
				return True
		return False
