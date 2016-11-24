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
from tkinter import *
from math import ceil
import threading

class DungeonMaster: 
	#TODO: add Inventory
	# initializes the Dungeon Master with the given input and output streams
	def __init__(self, master):
		self.numOfLines = 50

		#master widgets
		self.canvas1 = Canvas(master, scrollregion=(0,0,650,1350), borderwidth = 0, width = 650, height = 750, background = "#99ff99")
		self.scrollBar1 = Scrollbar(master, orient = "vertical", command = self.canvas1.yview)

		self.divider = Frame(master, height = 700, width = 20, bd = 1, 
			relief = RAISED, padx=5, pady=5, bg = "#ccccff")

		self.canvas2 = Canvas(master, scrollregion=(0,0,650,1350), borderwidth = 0, width = 650, height = 750, background = "#d9ff66")
		self.scrollBar2 = Scrollbar(master, orient = "vertical", command = self.canvas2.yview)

		self.entry1 = Entry(master, width = 121, bg = "#ccccff", font = ("Courier New", 12))
		self.entryButton1 = Button(master, text="submit", width = 15,
			height = 2, command = self.callback1_2, bg = "#ccccff")

		self.canvas1.grid(row = 0, column = 0, columnspan = 2, rowspan = 2)
		self.scrollBar1.grid(row = 0, column = 1, sticky = NE+SE)
		self.divider.grid(row = 0, column = 2)
		self.canvas2.grid(row = 0, column = 3, columnspan = 2, rowspan = 2)
		self.scrollBar2.grid(row = 0, column = 4, sticky = NE+SE)
		self.entry1.grid(row = 1, column = 0, ipady = 15, columnspan = 5, sticky = W)
		self.entryButton1.grid(row = 1, column = 4, sticky = E)

		self.canvas1.xview_moveto(0)
		self.canvas1.yview_moveto(600)
		self.canvas2.xview_moveto(0)
		self.canvas2.yview_moveto(600)

		self.frame1 = Frame(self.canvas1, height = 1350, width = 650, bg = "#99ff99" )
		self.canvas1.configure(yscrollcommand = self.scrollBar1.set)
		self.frame2 = Frame(self.canvas2, height = 1350, width = 650, bg = "#d9ff66" )
		self.canvas2.configure(yscrollcommand = self.scrollBar2.set)

		self.frame1.grid(row = 0, column = 0, sticky = N+S)
		self.canvas1.create_window((0,0), window = self.frame1, width = 650, height = 2650, tags = "self.frame1", anchor = "nw")
		self.frame2.grid(row = 0, column = 0, sticky = N+S)
		self.canvas2.create_window((0,0), window = self.frame2, width = 650, height = 2650, tags = "self.frame2", anchor = "nw")

		self.entry1.bind('<Return>', self.callback1_1)
		
		#frame widgets
		self.lines1 = [[Message(self.frame1, width = 640, bg = "#99ff99", font = ("Courier New", 12)), " " * 100] for i in range(self.numOfLines)]
		i = self.numOfLines-1
		for line in self.lines1:
			line[0].grid(row = i, column = 0, sticky = SW)
			line[0].config(text = line[1])
			i -= 1

		self.lines2 = [[Message(self.frame2, width = 640, bg = "#d9ff66", font = ("Courier New", 12)), " " * 100] for i in range(self.numOfLines)]
		i = self.numOfLines-1
		for line in self.lines2:
			line[0].grid(row = i, column = 0, sticky = W)
			line[0].config(text = line[1])
			i -= 1
		self.__Inventory = []
<<<<<<< HEAD
		self.__Lock  = threading.Lock()
=======
		self.__Lock = threading.Lock()
		self.screen1Lock = threading.Lock()
		self.screen2Lock = threading.Lock()
		self.command = ""
>>>>>>> 866cf041ca6921c01478d2d33af5b36515ba2842


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
		self.displayText("Done interrupting " + People[Character].name, ">> ", 1)
		return

	def print_options(self, dictionary):
		self.displayText("select a command:", ">", 1)
		self.entry1.unbind("<Return>")
		for key in dictionary:
			self.displayText((key + " - " + dictionary[key]), "", 1)
		self.entry1.bind("<Return>", self.get_option)
		return
		#self.entry1.bind("<Return>", lambda event, dictionary = dictionary: self.get_option(dictionary))

	def get_option(self, event):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.command = text
		self.entry1.unbind("<Return>")
		self.entry1.bind("<Return>", self.callback1_1)
		return

	# prints the menu
	def print_menu(self, Game_State):
<<<<<<< HEAD
		self.displayText("0 - Characters\n1 - Actions\n2 - Inventory\n3 - Everything\n", "", 1)
		"""
		if option in '0':
				#self.displayText(self.Game_State.Characters().keys(), ">> ", 1)
		elif option in '1':
				#self.displayText('i Name = Interrupt Name\np = Print Menu', ">> ", 1)
		elif option in '2':
				#self.displayText(self.__Inventory)
		elif option in '3':
				#print(Game_State.Characters, '\ni Name = Interrupt Name\np = Print Menu\n',
				#      self.__Inventory)
		"""
=======
		self.displayText("0 - Characters", "    ", 1)
		self.displayText("1 - Actions", "    ", 1)
		self.displayText("2 - Inventory", "    ", 1)
		self.displayText("3 - Everything", "    ", 1)
		self.entry1.unbind("<Return>")	
		#self.entry1.bind("<Return>", lambda event, arg=Game_State: self.print_menu_helper(event, arg))
		self.entry1.bind("<Return>", self.print_menu_helper)
		return

	def print_menu_helper(self, event):#, arg):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		if (text == '0'):
			for char in self.Game_State.Characters().keys():
				self.displayText(char, ">>", 1)
		elif (text == '1'):
			self.displayText('i Name = Interrupt Name', ">>", 1)
			self.displayText('p = Print Menu', ">> ", 1)
		elif (text == '2'):
			self.displayText("Inventory", ">>", 1)#self.__Inventory)
		elif (text == '3'):
			self.displayText("Characters:", ">", 1)
			for char in self.Game_State.Characters().keys():
				self.displayText(char, ">>", 1)
			self.displayText("Actions:", ">", 1)
			self.displayText('i Name = Interrupt Name', ">>", 1)
			self.displayText('p = Print Menu', ">> ", 1)
			self.displayText("Inventory", ">", 1)#self.__Inventory)
		else:
		    self.displayText("not a command", "", 1)
		self.entry1.unbind("<Return>")
		self.entry1.bind("<Return>", self.callback1_1)
>>>>>>> 866cf041ca6921c01478d2d33af5b36515ba2842
		return

	def lock_me():
		self.__Lock.acquire()
	def unlock_me():
		self.__Lock.release()

<<<<<<< HEAD
	def life(self, Game_State):
		while True:
			for (name, char)  in Game_State.Characters().items():
				print(name + " money: " + str(char.Money) + " event flag: " + str(char.Event.is_set()))
		


=======
	# Loops until Game is over
	def set_GameState(self, gs):
		self.Game_State = gs
	
>>>>>>> 866cf041ca6921c01478d2d33af5b36515ba2842
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
			lock = self.screen1Lock
		elif (screen == 2):
			displayFunction = self.displayText2
			lock = self.screen2Lock
		numLines = int(ceil((len(msgFrom) + 3 + len(message)) / 50))
		indent = " " * (len(msgFrom) + 2)
		line = msgFrom + ": " + message[0:50]
		lock.acquire()
		displayFunction(line)
		for i in range(numLines-2):	 
			line = indent + message[50*(i+1):50*(i+2)]
			displayFunction(line)
		if (numLines > 1):
			line = indent + message[(numLines-1)*50:len(message)]
			displayFunction(line)
<<<<<<< HEAD
		
=======
		lock.release()
>>>>>>> 866cf041ca6921c01478d2d33af5b36515ba2842


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
