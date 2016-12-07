"""
 Avita Sharma
 Game State Class

TODO: add Messaging
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
#		self.__Lock2      = threading.RLock()

#	def Lock(self):
#		return self.__Lock2

	def Messages(self):
		with self.__Lock:
			return self.__Messages

	def Window(self):
		with self.__Lock:
			return self.__window

	def Characters(self):
		with self.__Lock:
			return self.__Characters

	def Locations(self):
		with self.__Lock:
			return self.__Locations

	def set_Messages(self, Mess):
		with self.__Lock:
			self.__Messages = Mess

	def set_Messages(self, Mess):
		with self.__Lock:
			self.__Messages = Mess

	def set_Characters(self, Char):
		with self.__Lock:
			self.__Characters = Char

	def set_Locations(self, Loc):
		with self.__Lock:
			self.__Locations = Loc