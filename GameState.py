"""
 Avita Sharma, Eric Wyss, Davis Taus
 Game State Class
 A Collection of Shared Memory between the AI, GUI, and Battles.
""" 

import threading

"""
To change difficulty, change the wait times
(also number of characters spawned)

"""
LONGWAIT = 15
SHORTWAIT = 10
REALLYSHORTWAIT = 5

class GameState(object):

	def __init__(self, Messaging, Characters, Locations, Window):
		self.__Characters = Characters
		self.__Messages   = Messaging
		self.__Locations  = Locations
		self.__window     = Window
		self.__Lock       = threading.RLock()

	# call the function with the Game State Lock
	def withLock(self, fun, args=None):
		with self.__Lock:
			if args is not None:
				return fun(*args)
			else:
				return fun()

	# return the Game State Lock
	def Lock(self):
			return self.__Lock

	# return the Post Office
	def Messages(self):
		with self.__Lock:
			return self.__Messages

	# return the GUI Window
	def Window(self):
		with self.__Lock:
			return self.__window

	# return the Characters (AI and NPC):
	def Characters(self):
		with self.__Lock:
			return self.__Characters

	# return the Locations:
	def Locations(self):
		with self.__Lock:
			return self.__Locations