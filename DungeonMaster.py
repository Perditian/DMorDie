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

try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *

from tkinter import font

from math import ceil
import threading

class DungeonMaster: 
	#TODO: add Inventory
	# initializes the Dungeon Master with the given input and output streams
	def __init__(self, master):
		self.start_text = Text(master, padx = 250, insertwidth = 0, spacing1 = "80", font = font.Font(font = ("Courier New", 26, "normal")), bg = "#99ff99", relief = "flat", wrap = "word", width = 40, height = 4)
		self.start_text.tag_configure('tag-center', justify = 'center')
		self.start_text.insert('end', "Hi Dungeon Master, welcome to your new campaign! \nThere are characters for you to interrupt (i). \nYou can also print (p) a list of characters and actions if you forget. \nSpelling counts! \n", 'tag-center')
		self.start_text.grid(row = 0, column = 0)
		self.start_spacing = Frame(master, height = 100, bg = "#99ff99")
		self.start_spacing.grid(row = 1, column = 0)
		self.start_button = Button(master, text = "BEGIN", font = font.Font(font = ("Courier New", 14, "bold")), command = lambda: self.game_screen(master), width = 50, height = 4, bg = "#ccccff")		
		self.start_button.grid(row = 2, column = 0)


		self.numOfLines = 50
		self.__Inventory = []
		self.__Lock = threading.Lock()
		self.screen1Lock = threading.Lock()
		self.screen2Lock = threading.Lock()
		self.Event = threading.Event()
		self.command = ""
		self.narratorFont = font.Font(font = ("Courier New", 12, "bold"))
		self.otherFont = font.Font(font = ("Courier New", 12, "normal"))
		#self.Game_State.Characters
		self.shortcuts = {'r' : 'Rogue', 'a' : "Assasin", 'w' : 'Warrior'}
		self.styles = {'Rogue': ('#ff5050', self.otherFont), 'Assasin': ('#993366', self.otherFont), '': ('#000000', self.narratorFont), '<': ('#ff3300', self.otherFont), '>': ('#802b00', self.otherFont), '>>' : ('#ff00ff', self.otherFont), 'You' : ('#0000cc', self.otherFont), '    ' : ('#663300', self.otherFont), 'The Old Man' : ('#808080', self.otherFont), 'Anita Colbier' : ('#00ffcc', self.otherFont)}

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

		self.frame1 = Frame(self.canvas1, height = 1350, width = 650, bg = "#99ff99" )
		self.canvas1.configure(yscrollcommand = self.scrollBar1.set)
		self.frame2 = Frame(self.canvas2, height = 1350, width = 650, bg = "#d9ff66" )
		self.canvas2.configure(yscrollcommand = self.scrollBar2.set)

		self.lines1 = [[Message(self.frame1, width = 640, bg = "#99ff99", font = ("Courier New", 12)), " " * 100] for i in range(self.numOfLines)]
		self.lines2 = [[Message(self.frame2, width = 640, bg = "#d9ff66", font = ("Courier New", 12)), " " * 100] for i in range(self.numOfLines)]

		self.__Lock.acquire()



	def game_screen(self, master):
		self.__Lock.release()
		self.start_button.destroy()
		self.start_text.destroy()
		self.start_spacing.destroy()

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

		self.frame1.grid(row = 0, column = 0, sticky = N+S)
		self.canvas1.create_window((0,0), window = self.frame1, width = 650, height = 2650, tags = "self.frame1", anchor = "nw")
		self.frame2.grid(row = 0, column = 0, sticky = N+S)
		self.canvas2.create_window((0,0), window = self.frame2, width = 650, height = 2650, tags = "self.frame2", anchor = "nw")

		self.entry1.bind('<Return>', self.callback1_1)
		
		#frame widgets
		i = self.numOfLines-1
		for line in self.lines1:
			line[0].grid(row = i, column = 0, sticky = SW)
			line[0].config(text = line[1])
			i -= 1

		i = self.numOfLines-1
		for line in self.lines2:
			line[0].grid(row = i, column = 0, sticky = W)
			line[0].config(text = line[1])
			i -= 1

	# gets the next command
	def get_command(self, command):
		if re.match('i\s*\w*', command, re.I):
			Name = re.split('\s*', command)
			self.displayText(Name[len(Name) - 1], ">>", 1)
			return (self.interrupt, Name[len(Name) - 1])
		#elif re.match('p\s*', command, re.I):
		#	return (self.print_menu, self.Game_State)
		elif command == 'p' or command == 'P':
			return (self.print_menu, self.Game_State)
		elif command == 'pause' or command == 'Pause':
			self.__Lock.acquire()
			self.displayText("Game paused. Complete all pending interactions or they will fail. Type 'unpause' to resume.", "", 1)
		elif command == 'unpause' or command == 'Unpause':
			self.__Lock.release()
			self.displayText("Game resumed", "", 1)
		else:
			#print(self.__out, "I do not understand that command.\n")
			self.displayText("I do not understand that command.", ">>", 1)
		return (None, None)

	# interrupts the given Character
	# NOTE: interrupts should be synchronous (?) this prevents 
	# flooding the queue with interrupt messages and ensures that at most 
	# one interrupt will be on the messaging queue.
	def interrupt(self, Character):
		# unlock the Character's Event
		People = self.Game_State.Characters()
		try:
			People[self.shortcuts[Character]].Event.set()
		except KeyError:
			People[Character].Event.set()
		return

	def print_options(self, dictionary, prompt = "select a command:"):
		#with self.screen1Lock:
		self.displayText(prompt, ">", 1)
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
		self.Event.set()
		return

	# prints the menu
	def print_menu(self, Game_State):
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
			self.displayText('p = Print Menu', ">>", 1)
			self.displayText("Inventory", ">", 1)#self.__Inventory)
		else:
		    self.displayText("not a command", "", 1)
		self.entry1.unbind("<Return>")
		self.entry1.bind("<Return>", self.callback1_1)
		return

	def lock_me():
		self.__Lock.acquire()
	def unlock_me():
		self.__Lock.release()

	# Loops until Game is over
	def set_GameState(self, gs):
		self.Game_State = gs

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
		style = self.styles[msgFrom]
		if (screen == 1) :
			displayFunction = self.displayText1
			lock = self.screen1Lock
		elif (screen == 2):
			displayFunction = self.displayText2
			lock = self.screen2Lock
		numLines = int(ceil((len(msgFrom) + 3 + len(message)) / 55))
		indent = " " * (len(msgFrom) + 2)
		line = msgFrom + ": " + message[0:55]
		with lock:
			displayFunction(line, style)
			for i in range(numLines-2):	 
				line = indent + message[55*(i+1):55*(i+2)]
				displayFunction(line, style)
			if (numLines > 1):
				line = indent + message[(numLines-1)*55:len(message)]
				displayFunction(line, style)
		


	def displayText1(self, message, style):
		if (message == " "):
			return
		for i in range(self.numOfLines-2, 0, -1):
			lineAbove = self.lines1[i-1][1]
			prevColor = self.lines1[i-1][0].cget('fg')
			#prevSize = self.lines1[1-1][0].cget('size')
			prevFont = font.Font(font = self.lines1[i-1][0].cget('font'))
			self.lines1[i][1] = lineAbove
			self.lines1[i][0].config(text = lineAbove, fg = prevColor, font = prevFont)#, size = prevSize)
		newText = message
		self.lines1[0][0].config(text = newText, fg = style[0], font = style[1])#'-weight ' + style[1])
		self.lines1[0][1] = newText

	def callback2_1(self, event):
		text = self.entry2.get()
		self.entry2.delete(0, END)
		self.displayText(text, "You", 2)

	def callback2_2(self):
		text = self.entry2.get()
		self.entry2.delete(0, END)
		self.displayText(text, "You", 2)

	def displayText2(self, message, style):
		if (message == " "):
			return
		for i in range(self.numOfLines-2, 0, -1):
			lineAbove = self.lines2[i-1][1]
			prevColor = self.lines2[i-1][0].cget('fg')
			prevFont = font.Font(font = self.lines2[i-1][0].cget('font'))
			self.lines2[i][1] = lineAbove
			self.lines2[i][0].config(text = lineAbove, fg = prevColor, font = prevFont)
		newText = message
		self.lines2[0][0].config(text = newText, fg = style[0], font = style[1])#'-weight ' + style[1])
		self.lines2[0][1] = newText