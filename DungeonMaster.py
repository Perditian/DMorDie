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
from Tkinter import *
from math import ceil

class DungeonMaster: 
	#TODO: add Inventory
	# initializes the Dungeon Master with the given input and output streams
	def __init__(self, master):
		self.numOfLines = 27

		self.frame1 = Frame(master, height = 700, width = 690, bg = "#99ff99" )
		self.divider = Frame(master, height = 700, width = 20, bd = 1, 
			relief = RAISED, padx=5, pady=5, bg = "#ccccff")
		self.frame2 = Frame(master, height = 700, width = 690, bg = "#d9ff66")

		self.frame1.grid(row = 0, column = 0)
		self.divider.grid(row = 0, column = 1)
		self.frame2.grid(row = 0, column = 2)

		self.entry1 = Entry(master, width = 121, bg = "#ccccff", font = ("Courier New", 12))
		self.entry1.bind('<Return>', self.callback1_1)
		self.entry1.grid(row = 1, column = 0, ipady = 15, columnspan = 3, sticky = W)

		self.entryButton1 = Button(master, text="submit", width = 15,
			height = 2, command = self.callback1_2, bg = "#ccccff")
		self.entryButton1.grid(row = 1, column = 2, sticky = E)
		

		self.lines1 = [[Message(self.frame1, width = 640, bg = "#99ff99", font = ("Courier New", 12)), " " * 100] for i in range(self.numOfLines)]
		i = self.numOfLines-1
		for line in self.lines1:
			line[0].grid(row = i, column = 0, sticky = W)
			line[0].config(text = line[1])
			i -= 1

		self.lines2 = [[Message(self.frame2, width = 640, bg = "#d9ff66", font = ("Courier New", 12)), " " * 100] for i in range(self.numOfLines)]
		i = self.numOfLines-1
		for line in self.lines2:
			line[0].grid(row = i, column = 0, sticky = W)
			line[0].config(text = line[1])
			i -= 1
		self.__Inventory = []
		self.__Lock = threading.Lock()

	def set_GameState(self, gs):
		self.Game_State = gs

	# gets the next command
	def get_command(self, command):
		if re.match('i\s*\w*', command, re.I):
			Name = re.split('\s*', command)
			self.displayText(Name[len(Name) - 1], ">> ", 1)
			return (self.interrupt, Name[len(Name) - 1])
		elif re.match('p\s*', command, re.I):
			return (self.print_menu, self.Game_State)
		else:
			#print(self.__out, "I do not understand that command.\n")
			self.displayText("I do not understand that command.", ">> ", 1)
		return (None, None)

	# interrupts the given Character
	# NOTE: interrupts should be synchronous (?) this prevents 
	# flooding the queue with interrupt messages and ensures that at most 
	# one interrupt will be on the messaging queue.
	def interrupt(self, Character):
		# unlock the Character's Event
		People = self.Game_State.Characters()
		self.displayText("I am interrupting " + People[Character].name, ">> ", 1)#, Character)
		People[Character].Event.set()
		print People[Character].Event.is_set()
		self.displayText("Done interrupting " + People[Character].name, ">> ", 1)
		return

	# prints the menu
	def print_menu(self, Game_State):
		self.displayText("0 - Characters\n1 - Actions\n2 - Inventory\n3 - Everything\n", "", 1)
		"""
		if option in '0':
				#self.displayText(self.Game_State.Characters.keys(), ">> ", 1)
		elif option in '1':
				#self.displayText('i Name = Interrupt Name\np = Print Menu', ">> ", 1)
		elif option in '2':
				#self.displayText(self.__Inventory)
		elif option in '3':
				#print(Game_State.Characters, '\ni Name = Interrupt Name\np = Print Menu\n',
				 #      self.__Inventory)
		"""
		return

	def lock_me():
		self.__Lock.acquire()
	def unlock_me():
		self.__Lock.release()


    #######################################################################
    #######################################################################
	## WINDOW FUNCTIONS: ##################################################
	#######################################################################
	#######################################################################

	def callback1_1(self, event):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.displayText(text, "You", 1)
		(fun, args) = self.get_command(text)
		if fun == self.interrupt:
				self.interrupt(args)
		if fun == self.print_menu:
				self.print_menu(args)

	def callback1_2(self):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.displayText(text, "You", 1)
		(fun, args) = self.get_command(text)
		if fun == self.interrupt:
				self.interrupt(args)
		if fun == self.print_menu:
				self.print_menu(args)

	def displayText(self, message, msgFrom, screen):
		if (screen == 1) :
			displayFunction = self.displayText1
		elif (screen == 2):
			displayFunction = self.displayText2
		numLines = int(ceil((len(msgFrom) + 3 + len(message)) / 50))
		indent = " " * (len(msgFrom) + 2)

		line = msgFrom + ": " + message[0:50]
		displayFunction(line)
		for i in range(numLines-3):	 
			line = indent + message[50*(i+1):50*(i+2)]
			displayFunction(line)
		if (numLines > 1):
			line = indent + message[(numLines-1)*50:len(message)]
			displayFunction(line)


	def displayText1(self, message):#, msgFrom):
		for i in range(self.numOfLines-2, 0, -1):
			lineAbove = self.lines1[i-1][1]
			self.lines1[i][1] = lineAbove
			self.lines1[i][0].config(text = lineAbove)
		newText = message
		self.lines1[0][0].config(text = newText)
		self.lines1[0][1] = newText

	def callback2_1(self, event):
		text = self.entry2.get()
		self.entry2.delete(0, END)
		self.displayText(text, "You", 2)

	def callback2_2(self):
		text = self.entry2.get()
		self.entry2.delete(0, END)
		self.displayText(text, "You", 2)

	def displayText2(self, message):
		for i in range(self.numOfLines-2, 0, -1):
			lineAbove = self.lines2[i-1][1]
			self.lines2[i][1] = lineAbove
			self.lines2[i][0].config(text = lineAbove)
		newText = message
		self.lines2[0][0].config(text = newText)
		self.lines2[0][1] = newText
