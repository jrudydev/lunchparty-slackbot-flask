import random

ORGANIZER_INDEX = 0

FNAME_INDEX = 0
LNAME_INDEX = 1

CHANNEL_ID_INDEX = 0
CHANNEL_NAME_INDEX = 1
CHANNEL_TIMESTAMP_INDEX = 2

NUMBER_PER_GROUP = 4
MIN_GROUP_SIZE = 3


class User():
	'''
	Container class for a Slack user
	'''

	def __init__(self, user, handle, fname, lname):
		self.__user = user
		self.__handle = handle
		self.__name_tuple = (fname, lname)


	def get_user(self):
		return self.__user


	def get_handle(self):
		return self.__handle


	def get_name(self):
		first_name = self.__name_tuple[FNAME_INDEX]
		last_name = self.__name_tuple[LNAME_INDEX]

		names = []

		return " ".join(names)


	def get_link(self):
		return "<@" + self.__handle +  ">"


class LunchGroups():
	'''
	This class holds a list of users and can return a random list of grouped handles
	'''

	def __init__(self):
		self.__users = []
		self.__groups_list = []
		self.__join_channel = None
		self.__open_channel_tuples = []


	def clear_users(self):
		del self.__users[:]


	def clear_handles(self):
		del self.__groups_list[:]


	def clear_channel_tuples(self):
		self.__join_channel = None
		del self.__open_channel_tuples [:]


	def cancel(self):
		self.clear_users()
		self.clear_handles()
		self.clear_channel_tuples()


	def add_user(self, user):
		'''
		Add user if not already there
		'''

		handles = [participant.get_handle() for participant in self.__users]
		if user.get_handle() not in handles:
			self.__users.append(user)
			
			return user

		return None


	def remove_user(self, user):
		'''
		Remove user if exists
		'''

		handles = [participant.get_handle() for participant in self.__users]
		if user.get_handle() in handles:
			self.__users.remove(user)

			return user

		return None


	def get_user(self, handle):
		for user in self.__users:
			if user.get_handle() == handle:
				return user

		return None


	def get_users(self):
		return self.__users


	def get_organizer(self):
		if len(self.__users) > 0:
			return self.__users[ORGANIZER_INDEX]

		return None


	def get_organizer_channel_tuple(self):
		if len(self.__open_channel_tuples) > 0:
			return self.__open_channel_tuples[ORGANIZER_INDEX]

		return None
		

	def set_join_channel(self, cid, name,):
		self.__join_channel = (cid, name, "")


	def set_join_channel_timestamp(self, timestamp):
		channel_id = self.__join_channel[CHANNEL_ID_INDEX]
		channel_name = self.__join_channel[CHANNEL_NAME_INDEX]
		self.__join_channel = (channel_id, channel_name, timestamp)


	def get_join_channel_id(self):
		if self.__join_channel:
			return self.__join_channel[CHANNEL_ID_INDEX]

		return None


	def get_join_channel_timestamp(self):
		if self.__join_channel:
			return self.__join_channel[CHANNEL_TIMESTAMP_INDEX]

		return None


	def get_join_channel_link(self):
		channel_id = self.__join_channel[CHANNEL_ID_INDEX]
		channel_name = self.__join_channel[CHANNEL_NAME_INDEX]
		return "<#" + channel_id + "|" + channel_name + ">"


	def add_open_channel(self, cid, timestamp):
		channel_tuple = (cid, "", timestamp)
		self.__open_channel_tuples.append(channel_tuple)


	def get_open_channel_tuples(self):
		return self.__open_channel_tuples


	def get_open_channel_id(self, channel):
		return channel[CHANNEL_ID_INDEX]


	def get_open_channel_timestamp(self, channel):
		return channel[CHANNEL_TIMESTAMP_INDEX]


	def get_open_channel_link(self, channel):
		return "<#" + channel[CHANNEL_ID_INDEX] + "|" + channel[CHANNEL_NAME_INDEX] + ">"


	def set_random_handle_groups(self):
		'''
		Place the users in random groups
		'''

		self.clear_handles()

		handles = [participant.get_handle() for participant in self.__users]
		random.shuffle(handles)

		# slice groups list form random handles
		while len(handles) > 0:
			self.__groups_list.append(handles[:NUMBER_PER_GROUP])
			del handles[:NUMBER_PER_GROUP]

		if len(self.__groups_list) == 1:
			return

		# shift user around to meet minimum requirement
		last_group_list = self.__groups_list[-1:]
		last_group = last_group_list[0]
		number_of_left_overs = len(last_group)
		if number_of_left_overs < MIN_GROUP_SIZE:
			full_groups_list = self.__groups_list[:-1]
			if number_of_left_overs <= len(self.__groups_list[:-1]):
				# move left overs to full groups
				index = 0
				while len(last_group) > 0:
					self.__groups_list[index].append(last_group[0])
					del last_group[0]
					index += 1

				del self.__groups_list[-1:]
			else:
				# move from full group to left overs
				while len(full_groups_list[0]) > MIN_GROUP_SIZE:
					for x in range(0, len(full_groups_list)):
						last_group.append(full_groups_list[x][0])
						del full_groups_list[x][0]
						if len(last_group) >= MIN_GROUP_SIZE:
						 	break


	def get_handle_groups(self):
		'''
		Return the grouped handles
		'''

		return self.__groups_list



if __name__ == "__main__":
	handles = LunchGroups()
	handles.add_user(User("@rgom", "R123", "Rudy", "Gomez"))
	handles.add_user(User("@lcaz", "L123", "Lony", "Cazares"))
	handles.add_user(User("@dgom", "D123", "Dolores", "Gomez"))
	handles.add_user(User("@egom", "E123", "Edelmiro", "Gomez"))
	handles.add_user(User("@acaz", "A123", "Andy", "Cazares"))
	# handles.add_user(Participant("@bgom", "B123", "Ben", "Gomez"))
	# handles.add_user(Participant("@cgom", "C123", "Carmen", "Gomez"))
	handles.set_random_handle_groups()
	print(handles.get_handle_groups())


