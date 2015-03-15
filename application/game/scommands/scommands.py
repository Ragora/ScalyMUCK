"""
	Found here is a great example of how modifications are implemented inside of ScalyMUCK. All modifications that
	are intended to be loaded into ScalyMUCK must be provided in the form of a module you can merely drag and drop
	into application/game/ and from there the server host can modify their server_config.cfg file to add the modification
	to the loaded modification listing.

	This software is licensed under the MIT license.
	Please refer to LICENSE.txt for more information.
"""

import string

from blinker import signal

import game.models
import game.exception

class Modification:
	""" Main class object to load and initialize the scommands modification. """
	world = None
	interface = None
	session = None
	modloader = None

	pre_user_look = signal('pre_user_look')
	post_user_look = signal('post_user_look')
	pre_user_say = signal('pre_user_say')
	post_user_say = signal('post_user_say')
	pre_user_pose = signal('pre_user_pose')
	post_user_pose = signal('post_user_pose')
	pre_item_pickup = signal('pre_item_pickup')
	post_item_pickup = signal('post_item_pickup')
	pre_item_drop = signal('pre_item_drop')
	post_item_drop = signal('post_item_drop')
	post_user_create = signal('post_user_create')
	pre_exit_room = signal('pre_exit_room')
	post_exit_room = signal('post_exit_room')
	pre_show_description = signal('pre_show_description')

	def initialize(self, **kwargs):
		""" 

		This initializes an instance of the scommands modification and it will remain loaded in memory

		until the server owner either unloads it or reloads it which therefore will reset
		any associated data unless the data had been defined on the class definition itself
		rather than being initialized in this function. 


		Keyword arguments:
			* config -- This is the instance of Settings that contains all loaded configuration settings available for this modification, if the file exists. If the file does not exist, then this will simply be None.
			* interface -- This is the instance of the user interface used internally by ScalyMUCK. Generally, you won't need access to this for any reason and is currently deprecated for later removal.


		Actions such as binding your Blinker signals should be performed here so that events will be
		received properly when they occur.

		Along with initializing the modification, __init__ acts as a gateway for other important

		data passed in by the modloader under the **kwargs argument.

		"""

		self.config = kwargs['config']
		self.interface = kwargs['interface']
		self.session = kwargs['session']
		self.world = kwargs['world']
		self.permissions = kwargs['permissions']
		self.modloader = kwargs['modloader']

		signal('post_client_authenticated').connect(self.callback_client_authenticated)
		signal('pre_message_sent').connect(self.callback_message_sent)
		
	def __del__(self):
		signal('post_client_authenticated').disconnect(self.callback_client_authenticated)
		signal('pre_message_sent').disconnect(self.callback_message_sent)

	# Commands
	def command_say(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']

		if (input == ''):
			sender.send('Usage: say <message>')
			return

		results = self.pre_user_say.send(None, sender=sender, input=input)
		for result in results:
			if (result[1] is True):
				return

		sender.location.broadcast('%s says, "%s"' % (sender.display_name, input), sender)
		sender.send('You say, "%s"' % (input))
		self.post_user_say.send(None, sender=sender, input=input)

	def command_pose(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']
		results = self.pre_user_pose.send(None, sender=sender, input=input)
		for result in results:
			if (result[1] is True):
				return

		sender.location.broadcast('%s %s' % (sender.display_name, kwargs['input']))
		self.post_user_pose.send(None, sender=sender, input=input)

	def command_look(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']
		target = sender.location
		name = sender.location.name

		self.pre_user_look.send(sender=sender, input=input)

		if (input != ''):
			target = sender.location.find_player(name=input)
			if (target is None):
				target = sender.location.find_bot(name=input)

			if (target is not None):
				name = target.display_name
				if (type(target) is game.models.Player):
					target.send('++++++++ %s is looking at you!' % (sender.display_name))
			else:
				target = sender.location.find_item(name=input)
				if (target is None):
					target = sender.inventory.find_item(name=input)

				if (target is not None):
					name = target.name
				else:
					sender.send('I do not see that.')
					return
		sender.send('<' + name + '>')

		if (type(target) is game.models.Room):
			sender.send('Obvious Exits: ')
			if (len(target.exits) != 0):
				for exit in target.exits:
					sender.send('	%s' % (exit.name))
			else:
				sender.send('	None')

			sender.send('People: ')
			for player in target.players:
				sender.send('	%s' % (player.display_name))

			sender.send('Bots: ')
			if (len(target.bots) != 0):
				for bot in target.bots:
					sender.send('	%s' % (bot.display_name))
			else:
				sender.send('	None')

			sender.send('Items: ')
			if (len(target.items) != 0):
				for item in target.items:
					sender.send('	%s' % (item.name))
			else:
				sender.send('	None')

		self.pre_show_description.send(None, sender=sender, target=target)
		sender.send('Description:')
		sender.send(target.description)

		self.post_user_look.send(sender=sender, input=input, target=target)

	def command_move(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']

		if (input == ''):
			sender.send('Usage: move <name of exit>')
			return

		exit = sender.location.find_exit(name=input)
		if (exit is not None):
			sender.send(exit.user_enter_message)
			sender.location.broadcast('%s %s' % (sender.display_name, exit.room_enter_message), sender)
			results = self.pre_exit_room.send(None, sender=sender, target=exit.target_id)
			for result in results:
				if (result[1] is True):
					return
			sender.set_location(exit.target_id)
			sender.location.broadcast('%s %s' % (sender.display_name, exit.room_exit_message), sender)
			sender.send(exit.user_exit_message)
			self.command_look(sender=sender, input='')
			self.post_exit_room.send(None, sender=sender, target=sender.location)
		else:
			sender.send('I do not see that.')

	def command_inventory(self, **kwargs):
		sender = kwargs['sender']

		sender.send('Items:')
		if (len(sender.inventory.items) != 0):
			for item in sender.inventory.items:
				sender.send('	%s' % (item.name))
		else:
			sender.send('	None')

		# Pocket dimension anybody?
		if (len(sender.inventory.players) != 0):
			sender.send('People: ')
			for player in sender.inventory.players:
				sender.send('	%s' % (player.display_name))

	def command_take(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']

		if (input == ''):
			sender.send('Usage: take <object name>')
			return

		item = sender.location.find_item(name=input)
		if (item is not None):
			results = self.pre_item_pickup.send(None, sender=sender, item=item)
			for result in results:
				if (result[1] is True):
					return

			sender.send('Taken.')

			item.set_location(sender.inventory)
			self.post_item_pickup.send(None, sender=sender, item=item)
		else:
			sender.send('I do not see that.')

	def command_passwd(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']

		if (input == ''):
			sender.send('Usage: passwd <password>')
			return

		sender.set_password(input)
		sender.send('Your password has been changed. Remember it well.')

	def command_drop(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']

		if (input == ''):
			sender.send('Usage: drop <item name>')
			return

		item = sender.inventory.find_item(name=input)
		if (item is not None):
			results = self.pre_item_drop.send(sender=sender, item=item)
			for result in results:
				if (result[1] is True):
					return

			item.set_location(sender.location)
			sender.send('You dropped a/an %s.' % (item.name ))
			sender.location.broadcast('%s drops a/an %s.' % (sender.display_name, item.name), sender)
			self.post_item_drop.send(sender=sender, item=item)
		else:
			sender.send('I see no such item.')

	def command_help(self, **kwargs):
		sender = kwargs['sender']
		input = kwargs['input']

		sender.send('For more information, type: help <command/category>')

		if (input == ''):
			sender.send('Available command categories:')
			categories = []
			for command in self.modloader.commands:
				privilege = self.modloader.commands[command]['privilege']
				if ((privilege == 1 and sender.is_admin is False) or (privilege == 2 and sender.is_sadmin is False) or (privilege == 3 and sender.is_owner is False)):
					continue

				if ('category' in self.modloader.commands[command]):
					category = self.modloader.commands[command]['category']
					if (category not in categories):
						categories.append(category)
						sender.send('\t+ ' + category)
				elif ('Unclassed' not in categories):
					categories.append('Unclassed')
					sender.send('\t+ Unclassed')

			
		else:
			l_input = input.lower()
			if (input not in self.modloader.commands):
				category_contents = [ ]

				for command in self.modloader.commands:
					privilege = self.modloader.commands[command]['privilege']
					if ((privilege == 1 and sender.is_admin is False) or (privilege == 2 and sender.is_sadmin is False) or (privilege == 3 and sender.is_owner is False)):
						continue

					if ('category' in self.modloader.commands[command]):
						category = self.modloader.commands[command]['category']
						if (category.lower() == l_input):
							category_contents.append(command)
					elif (l_input == 'unclassed'):
						category_contents.append(command)

				if (len(category_contents) == 0):
					sender.send('No such command or category: %s' % input)
				else:
					sender.send('Available commands in category %s:' % input)
					for command_name in category_contents:
						sender.send('\t+ %s - %s' % (command_name, self.modloader.commands[command_name]['description']))
			else:
				privilege = self.modloader.commands[l_input]['privilege']
				if ((privilege == 1 and sender.is_admin is False) or (privilege == 2 and sender.is_sadmin is False) or (privilege == 3 and sender.is_owner is False)):
					sender.send('No such command or category: %s' % input)
					return

				sender.send('From: %s' % (self.modloader.commands[input]['modification']))
				sender.send('Usage: %s' % (self.modloader.commands[input]['usage']))
				sender.send(self.modloader.commands[input]['description'])


	def command_quit(self, **kwargs):
		sender = kwargs['sender']
		sender.disconnect()

	def command_froguser(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['arguments']
		if (len(args) < 1):
			sender.send('Usage: frog <name>')
			return

		name = args[0]
		target = self.world.find_player(name=string.lower(name))
		if (target is not None):
			if (target is sender):
				sender.send('That is yourself!')
				return
			elif (target.is_sadmin ==1 or target.is_owner == 1):
				sender.send('You cannot do that, they are too powerful.')
				return
			else:
				sender.send('User "%s" frogged. Check your inventory.' % (target.display_name))
				sender.location.broadcast('%s has turned %s into a small plastic figurine, never to move again.' % (sender.display_name, target.display_name), sender, target)
				item = self.world.create_item(target.display_name, target.description, sender, sender.inventory)
				target.send('%s has turned you into a small plastic figurine, never to move again and discreetly places you in their inventory.' % (sender.display_name))
				target.delete()
		else:
			sender.send('User "%s" does not exist anywhere.' % (name))

	def command_adduser(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['arguments']
		if (len(args) < 2):
			sender.send('Usage: adduser <name> <password>')
			return

		name = args[0]
		password = args[1]

		if (self.world.find_player(name=string.lower(name)) is not None):
			sender.send('User already exists.')
			return

		# TODO: Make this take server prefs into consideration, and also let this have a default location ...
		player = self.world.create_player(name, password, game.models.server.work_factor, sender.location)
		sender.send('User "%s" created.' % (name))
		self.post_user_create.send(None, creator=sender, created=player)
		
	def command_admin(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['arguments']
		if (len(args) < 1):
			sender.send('Usage: admin <name>')
			return

		name = args[0]

		target = self.world.find_player(name=string.lower(name))
		if (target is not None):
			if (target is sender):
				sender.send('That is yourself!')
				return
			elif (sender.check_admin_trump(target) is False):
				sender.send('You cannot do that. They are too strong.')
				target.send('%s tried to take your administrator privileges away.' % (sender.display_name))
				return

			target.set_is_admin(target.is_admin is False)
			if (target.is_admin == 0):
				sender.send('%s is no longer an administrator.' % (target.display_name))
				target.send('%s took your adminship.' % (sender.display_name))
				return
			else:
				sender.send('%s is now an administrator.' % (target.display_name))
				target.send('%s gave you adminship rights.' % (sender.display_name))
				return
			sender.send('Unknown user.')

	def command_sadmin(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['arguments']
		if (len(args) < 1):
			sender.send('Usage: sadmin <name>')
			return

		name = args[0]

		target = self.world.find_player(name=string.lower(name))
		if (target is not None):
			if (target is sender):
				sender.send('That is yourself!')
				return
			elif (sender.check_admin_trump(target) is False):
				sender.send('You cannot do that. They are too strong.')
				target.send('%s tried to take your super administrator privileges away.' % (sender.display_name))
				return

			target.set_is_super_admin(target.is_sadmin is False)
			if (target.is_sadmin is False):
				sender.send('%s is no longer a super administrator.' % (target.display_name))
				target.send('%s took your super adminship.' % (sender.display_name))
				return
			else:
				sender.send('%s is now a super administrator.' % (target.display_name))
				target.send('%s gave you super adminship rights.' % (sender.display_name))
				return
			sender.send('Unknown user.')

	def command_chown(self, **kwargs):
		sender = kwargs['sender']
		args = kwargs['arguments']

		if (len(args) < 2):
			sender.send('Usage: chown <item name> <new owner>')
			return

		item_name = args[0]
		owner_name = args[1]

		item = sender.inventory.find_item(name=item_name)
		if (item.owner_id != sender.id):
			sender.send('This is not your item.')
			return

		player = self.world.find_player(name=owner_name)
		if (player is None):
			sender.send('There is no such player.')
		else:
			item.set_owner(player)
			sender.send('%s now owns that item.' % (player.display_name))
			player.send('%s has given you a %s.' % (sender.display_name, item.name))

	def command_ping(self, **kwargs):
		kwargs['sender'].send('Pong.')

	def command_wwi(self, **kwargs):
		sender = kwargs['sender']

		listing = self.interface.get_online_players()
		longest_length = 0
		for player in listing:
			length = len(player.display_name)
			if (length > longest_length):
				longest_length = length

		spacing = ''
		for i in range(longest_length+7):
			spacing += ' '

		sender.send('Name%sLocation' % spacing)
		for player in listing:
			spacing = ''
			for i in range((longest_length+11)-len(player.display_name)):
				spacing += ' '
			sender.send('%s%s%s' % (player.display_name, spacing, player.location.name))
		sender.send('Who/Where/Idle')

	# Callbacks
	def callback_client_authenticated(self, trigger, sender):
		""" Callback that is bound to the "post_client_authenticated" event.

		Callbacks like this one are helpful in cases that if you want to initialize
		certain data upon the authentication of a certain client -- perhaps you're loading
		mod data that is related to this client.

		Refer to the :command:`__init__` function.

		"""
		self.command_look(sender=sender, input='')

	def callback_message_sent(self, trigger, sender, input):
		""" Callback that is bound to the "pre_message_sent" event.

		Callbacks like this one are helpful in cases that if you want to intercept
		input for any reason, such as an interactive menu that will handle it's own
		text parsing for handling menu functions as that if the callback at any point
		returns true, the server will not pass the input text into the core parser.

		Refer to the :command:`__init__` function.

		"""
		if (len(input) != 0):
			if (input[0] == ':'):		
				self.command_pose(sender=sender, input=input[1:].lstrip())
				return True
			elif (input[0] == '"'):
				self.command_say(sender=sender, input=input[1:].lstrip())
				return True

		return False

	def get_commands(self):
		""" Returns a dictionary mapping the available commands in this modification.

		This is a function call merely for the purpose of being able to provide variable
		output, so that if the modification has an accompanying configuration file it can
		omit or include certain commands based on the configuration settings loaded in the
		modification's :command:`__init__` function.

		"""
		command_dict = {
			'say': 
			{ 
				'command': self.command_say,
				'description': 'Makes you say something. Only visible to the current room you\'re in.',
				'usage': 'say <arbitrary text> | "<arbitrary text>',
				'aliases': [ 'speak' ],
				'privilege': 0,
				'category': 'General'
			},

			'pose': 
			{
				'command': self.command_pose,
				'description': 'Used to show arbitrary action. Only visible to the current room you\'re in.',
				'usage': 'pose <arbitrary pose> | :<arbitrary pose>',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},

			'look': 
			{
				'command': self.command_look,
				'description': 'Get your bearings. Look around in the local area to see what you can see.',
				'usage': 'look [room name | item name | player name]',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},
		
			'move':
			{
				'command': self.command_move,
				'description': 'Moves to a new location.',
				'usage': 'move <exit name>',
				'aliases': [ 'go' ],
				'privilege': 0,
				'category': 'General'
			},

			'inventory':
			{
				'command': self.command_inventory,
				'description': 'View your inventory.',
				'usage': 'inventory',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},

			'take':
			{
				'command': self.command_take,
				'description': 'Take an item from the current room.',
				'usage': 'take <item>',
				'aliases': [ 'get' ],
				'privilege': 0,
				'category': 'General'
			},

			'passwd':
			{
				'command': self.command_passwd,
				'description': 'Changes your password.',
				'usage': 'passwd <new password>',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},

			'drop':
			{
				'command': self.command_drop,
				'description': 'Drops an item from your inventory.',
				'usage': 'drop <item name>',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},

			'help':
			{
				'command': self.command_help,
				'description': 'Displays the help text.',
				'usage': 'help [command name]',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},

			'quit':
			{
				'command': self.command_quit,
				'description': 'Drops your connection from the server.',
				'usage': 'quit',
				'aliases': [ 'leave' ],
				'privilege': 0,
				'category': 'General'
			},

			'frog':
			{
				'command': self.command_froguser,
				'description': 'Deletes a user from the world -- making them an item in your inventory to with as you please.',
				'usage': 'frog <player name>',
				'aliases': [ ],
				'privilege': 2,
				'category': 'Administration'
			},

			'adduser':
			{
				'command': self.command_adduser,
				'description': 'Creates a new player in the world.',
				'usage': 'adduser <name> <password>',
				'aliases': [ ],
				'privilege': 2,
				'category': 'Administration'
			},

			'admin':
			{
				'command': self.command_admin,
				'description': 'Toggles the admin status of a specified player.',
				'usage': 'admin <name>',
				'aliases': [ ],
				'privilege': 1,
				'category': 'Administration'
			},

			'sadmin':
			{
				'command': self.command_sadmin,
				'description': 'Toggles the super admin status of a specified player.',
				'usage': 'sadmin <name>',
				'aliases': [ ],
				'privilege': 2,
				'category': 'Administration'
			},

			'chown':
			{
				'command': self.command_chown,
				'description': 'Transfers ownership of an item in your inventory or in the room to a specified player providied you are the original owner.',
				'usage': 'chown <item name> <new owner name>',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},

			'ping':
			{
				'command': self.command_ping,
				'description': 'Ping-Pong.',
				'usage': 'ping',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			},

			'wwi':
			{
				'command': self.command_wwi,
				'description': 'See a list of connected people.',
				'usage': 'wwi',
				'aliases': [ ],
				'privilege': 0,
				'category': 'General'
			}
		}
		return command_dict
