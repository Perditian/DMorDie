"""
 Avita Sharma
 Dungeon Master Class

TODO: add Messaging
""" 

from AI import AI 
from Action import Action
import threading
import random
import GameState
import sys
import re
import time

class DungeonMaster: 
	#TODO: add Inventory
	# initializes the Dungeon Master with the given input and output streams
	def __init__(self, Input, Output):
		self.__in = Input
		self.__out = Output
		self.__Inventory = []
		self.__Lock = threading.Lock()

		# Make a thread that waits for user input:



	# gets the next command
	def get_command(self, command):
		if re.match('i\s*\w*', command, re.I):
			Name = re.split('\s*', command)
			print(Name[len(Name) - 1])
			return (self.interrupt, Name[len(Name) - 1])
		elif re.match('p\s*', command, re.I):
			return (self.print_menu, None)
		else:
			#print(self.__out, "I do not understand that command.\n")
			print("I do not understand that command.\n")
		return (None, None)

	# interrupts the given Character
	# NOTE: interrupts should be synchronous (?) this prevents 
	# flooding the queue with interrupt messages and ensures that at most 
	# one interrupt will be on the messaging queue.
	def interrupt(self, Game_State, Character):
		# unlock the Character's Event
		print("I am interrupting ", Character)
		Person = (Game_State.Characters())[Character]
		# Person.event.set()
		print("Done interrupting")
		return

	# prints the menu
	def print_menu(self, Game_State):
		print(self.__out, "0 - Characters\n1 - Actions\n2 - Inventory\n3 - Everything\n")
		option = sys.stdin.readline()
		if option in '0':
				print(Game_State.Characters)
		elif option in '1':
				print('i Name = Interrupt Name\np = Print Menu')
		elif option in '2':
				print(self.__Inventory)
		elif option in '3':
				print(Game_State.Characters, '\ni Name = Interrupt Name\np = Print Menu\n',
				       self.__Inventory)
		return

	def lock_me():
		self.__Lock.acquire()
	def unlock_me():
		self.__Lock.release()

	# Loops until Game is over
	def life(self, Game_State):
			(fun, args) = self.get_command(line)
			if fun == self.interrupt:
				self.interrupt(Game_State, args)
			if fun == self.print_menu:
				self.print_menu(Game_State)