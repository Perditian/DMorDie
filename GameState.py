"""
 Avita Sharma
 Game State Class

TODO: add Messaging
""" 

from AI import AI 
from Action import Action
import threading
import random

class GameState:

	def __init__(self, Messaging, Characters, Locations):
		self.__Characters = Characters
		self.__Messages = Messaging
		self.__Locations = Locations
		self.__Lock = threading.Lock()

	def Messages(self):
		with self.__Lock:
			return self.__Messages

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