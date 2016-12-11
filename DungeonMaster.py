"""
 Avita Sharma, Eric Wyss, Davis Taus
 Dungeon Master (Window GUI) Class

""" 

from AI import AI 
from Action import Action
import threading
import random
import GameState
import sys
import re
import time
from idlelib.WidgetRedirector import WidgetRedirector

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
	#define widgets and variables
	def __init__(self, master):
		#startsceen widget creation and placement
		self.start_text = Text(master, insertwidth = 0, spacing1 = "45", 
			font = font.Font(font = ("Courier New", 22, "normal")), 
			bg = "#1a0d00", fg = "#ff8000", relief = "flat", wrap = "word",
			width = 40, height = 8)
		self.start_text.tag_configure('tag-center', justify = 'center')

		#opening text
		startText = ("Hi Dungeon Master, welcome to your new campaign! \nThere" 
			" are characters for you to interrupt (i). \nYou can also print (p)" 
			" a list of characters and actions if you forget. \n Spelling "
			"counts! \nYou can pause/unpause the game by typing 'pause' "
			"or 'unpause'\n")
		self.start_text.insert('end', startText, 'tag-center')

		#widget placement
		self.start_text.place(relx = 0.5, rely = 0.4, anchor = CENTER)
		self.start_button = Button(master, text = "BEGIN", 
			font = font.Font(font = ("Courier New", 14, "bold")), 
			command = lambda: self.game_screen(master), 
			width = 50, height = 4, fg = "#1a0500",bg = "#ff704d")		
		self.start_button.place(relx = 0.5, rely = 0.85, anchor = CENTER)

		
		#self.__Inventory = []
		#window lock for pausing game
		self.__Lock = threading.Lock()
		#locks to gain exclusive access to each screen
		self.screen1Lock = threading.Lock()
		self.screen2Lock = threading.Lock()

		self.Event = threading.Event()
		self.command = ""

		#style options
		self.narratorFont = font.Font(font = ("Courier New", 12, "bold"))
		self.otherFont = font.Font(font = ("Courier New", 12, "normal"))
		#TODO: pool of fonts, create fonts at beginning in function with 
		#parameters chars
		self.shortcuts = {}

		self.styles = {'Rogue': ('#ff5050', self.otherFont, 'r'), 
			'Assassin': ('#66a3ff', self.otherFont, 'a'), 
			'': ('#fff2e6', self.narratorFont), 
			'': ('#ff3300', self.otherFont), 
			'>': ('#ffb066', self.otherFont), 
			'<' : ('#ff00ff', self.otherFont), 
			'You' : ('#e6e6ff', self.otherFont), 
			'    ' : ('#663300', self.otherFont), 
			'TheOldMan' : ('#9999ff', self.otherFont), 
			'AnitaColbier' : ('#ffa64d', self.otherFont),
			'Barbarian': ("#D0A9F5", self.otherFont, 'b'),
			'Knight': ("#F3E2A9", self.otherFont, 'k'),
			'>>': ('#e6e6ff', self.otherFont)}
		self.screen1Color = "#331a00"
		self.screen2Color = "#330a00"

		#master widgets
		self.canvas1 = Canvas(master, scrollregion=(0,0,650,1350), 
			borderwidth = 0, width = 650, height = 750, background = "#99ff99")
		self.scrollBar1 = Scrollbar(master, orient = "vertical", 
			command = self.canvas1.yview)

		self.divider = Frame(master, height = 700, width = 20, 
			relief = RAISED, padx=5, pady=5, bg = "#ff8400")

		self.canvas2 = Canvas(master, scrollregion=(0,0,650,1350), 
			borderwidth = 0, width = 650, height = 750, background = "#ffe6cc")
		self.scrollBar2 = Scrollbar(master, orient = "vertical", 
			command = self.canvas2.yview)

		#entry region and button
		self.entry1 = Entry(master, width = 121, bg = "#ffe6cc", 
			font = ("Courier New", 12))
		self.entryButton1 = Button(master, text="submit", width = 15, 
			font = self.otherFont, fg = "#1a0500", height = 2, 
			command = self.callback1_2, bg = "#ff704d")

		#frames holding textboxes
		self.frame1 = Frame(self.canvas1, height = 1350, width = 650, 
			bg = self.screen1Color )
		self.canvas1.configure(yscrollcommand = self.scrollBar1.set)
		self.frame2 = Frame(self.canvas2, height = 1350, width = 650, 
			bg = self.screen2Color )
		self.canvas2.configure(yscrollcommand = self.scrollBar2.set)

		#textboxes
		self.text1 = ReadOnlyText(self.canvas1, wrap = WORD, padx = 10, 
			height = 1350, bg = self.screen1Color, 
			font = self.narratorFont, fg = '#fff2e6')
		self.text2 = ReadOnlyText(self.canvas2, wrap = WORD, padx =10, 
			height = 1350, bg = self.screen2Color, 
			font = self.narratorFont, fg = '#fff2e6')

		#set tags for text style
		self.tags()

		#lock window for startscreen
		self.__Lock.acquire()


	#destroy startscreen widgets and replace with game widgets
	def game_screen(self, master):
		#release lock for AI to start actions
		self.__Lock.release()
		self.start_button.destroy()
		self.start_text.destroy()

		#widget placement
		self.canvas1.grid(row = 0, column = 0, columnspan = 2, rowspan = 2)
		self.scrollBar1.grid(row = 0, column = 1, sticky = NE+SE)
		self.divider.grid(row = 0, column = 2)
		self.canvas2.grid(row = 0, column = 3, columnspan = 2, rowspan = 2)
		self.scrollBar2.grid(row = 0, column = 4, sticky = NE+SE)
		self.entry1.grid(row = 1, column = 0, ipady = 15, columnspan = 5, 
			sticky = W)
		self.entryButton1.grid(row = 1, column = 4, sticky = E)

		#initial view bottom of textbox
		self.canvas1.xview_moveto(0)
		self.canvas1.yview_moveto(600)
		self.canvas2.xview_moveto(0)
		self.canvas2.yview_moveto(600)

		#placement
		self.text1.grid(row = 0, column = 0, sticky = N+S)
		self.canvas1.create_window((0,0), window = self.text1, width = 650,
			height = 1300, tags = "self.frame1", anchor = "nw")
		self.text2.grid(row = 0, column = 0, sticky = N+S)
		self.canvas2.create_window((0,0), window = self.text2, width = 650, 
			height = 1300, tags = "self.frame2", anchor = "nw")

		self.entry1.bind('<Return>', self.callback1_1)

		#to have text start printing from bottom
		self.text1.insert(END, ' \n' * 100)
		self.text2.insert(END, ' \n' * 100)

		#create shortcuts for characters
		for char in self.Game_State.Characters().keys():
			if self.Game_State.Characters()[char].fighter:
				if not (char in self.shortcuts):
					self.shortcuts[char[0].lower()] = char
				else:
					duplicate = true
					i = 2
					while (duplicate):
						if char.lower()+str(i) in self.shortcuts:
							i+= 1
						else:
							self.shortcuts[char[0].lower()+str(i)] = char

	#sets tags for textbox so each character has unique style
	def tags(self):
		for char in self.styles:
			self.text1.tag_configure(char, foreground = self.styles[char][0], 
				font = self.styles[char][1])
			self.text2.tag_configure(char, foreground = self.styles[char][0], 
				font = self.styles[char][1])


	# gets the next command
	# i (name): interrupts char to interact
	# p: prints printmenu
	# pause: pause game
	def get_command(self, command):
		if re.match('i\s*\w*', command, re.I):
			Name = re.split('\s*', command)
			self.displayText(Name[len(Name) - 1], ">>", 1)
			return (self.interrupt, Name[len(Name) - 1])
		elif command == 'p' or command == 'P':
			return (self.print_menu, self.Game_State)
		elif command == 'pause' or command == 'Pause':
			self.__Lock.acquire()
			pauseText = ("Game paused. Complete all pending interactions or"
				" they will fail. Type 'unpause' to resume.")
			self.displayText(pauseText, "", 1)
		elif command == 'unpause' or command == 'Unpause':
			self.__Lock.release()
			self.displayText("Game resumed", "", 1)
		else:
			self.displayText("I do not understand that command.", ">>", 1)
		return (None, None)

	# interrupts the given Character
	# this prevents 
	# flooding the queue with interrupt messages and ensures that at most 
	# one interrupt will be on the messaging queue.
	def interrupt(self, Character):
		# unlock the Character's Event
		People = self.Game_State.Characters()
		try:
			People[Character].Event.set()
		except KeyError:
			try:
				People[self.shortcuts[Character]].Event.set()
			except KeyError:
				try:
					People[Character.capitalize()].Event.set()
				except KeyError:
					self.displayText("I do not recognize that name.", ">>", 1)
		return

	#takes in dictionary and displays all key value pairs
	def print_options(self, dictionary, prompt = "select a command:"):
		#with self.screen1Lock:
		self.displayText(prompt, ">", 1)
		self.entry1.unbind("<Return>")
		for key in dictionary:
			self.displayText((key + " - " + dictionary[key]), "", 1)
		self.entry1.bind("<Return>", self.get_option)
		return

	#gets and stores text in textbox under command, 
	#and rebinds to standard callback
	def get_option(self, event):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.command = text
		self.entry1.unbind("<Return>")
		self.entry1.bind("<Return>", self.callback1_1)
		self.Event.set()
		return

	# prints the menu and binds next entry to print_menu_helper
	def print_menu(self, Game_State):
		self.displayText("0 - Characters", "    ", 1)
		self.displayText("1 - Actions", "    ", 1)
		self.displayText("2 - Inventory", "    ", 1)
		self.displayText("3 - Everything", "    ", 1)
		self.entry1.unbind("<Return>")	
		self.entry1.bind("<Return>", self.print_menu_helper)
		return

	#reads in command after the print menu is displayed and
	#prints out the correct information
	def print_menu_helper(self, event):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		if (text == '0'):
			for char in self.Game_State.Characters().keys():
				if (len(self.styles[char]) == 3):
					self.displayText(char + "- shortcut: " + 
						self.styles[char][2], ">>", 1)
				else:
					self.displayText(char, ">>", 1)
		elif (text == '1'):
			self.displayText('i Name = Interrupt Name', ">>", 1)
			self.displayText('p = Print Menu', ">> ", 1)
			self.displayText('pause = Pause', ">>", 1)
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

	#upon pressing enter gets text, clears textbox, and calls get_command 
	#on text to parse, then calls correct function
	def callback1_1(self, event):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.displayText(text, "You", 1)
		(fun, args) = self.get_command(text)
		if fun == self.interrupt:
				self.interrupt(args)
		if fun == self.print_menu:
				self.print_menu(args)

	#callback1_1 for submit button
	def callback1_2(self):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.displayText(text, "You", 1)
		(fun, args) = self.get_command(text)
		if fun == self.interrupt:
				self.interrupt(args)
		if fun == self.print_menu:
				self.print_menu(args)

	#function to print to screen, formats text and calls function
	#to display text on the desired screen with its lock
	def displayText(self, message, msgFrom, screen):
#		style = self.styles[msgFrom]
		line = msgFrom + ": " + message + "\n"
		if (screen == 1) :
			displayFunction = self.displayText1
			lock = self.screen1Lock
		elif (screen == 2):
			displayFunction = self.displayText2
			lock = self.screen2Lock
		with lock:
			displayFunction(line, msgFrom)
		
	#print to screen1, scroll to see most recent entry
	def displayText1(self, message, msgFrom):
		if (message == " "):
			return
		self.text1.insert(END, message, msgFrom)
		self.text1.see(END)
	
	#print to screen2, scroll to see most recent entry
	def displayText2(self, message, msgFrom):
		if (message == " "):
			return
		self.text2.insert(END, message, msgFrom.replace(" ",""))
		self.text2.see(END)

	#callback1_1 for second screen
	def callback2_1(self, event):
		text = self.entry2.get()
		self.entry2.delete(0, END)
		self.displayText(text, "You", 2)

	#callback for second screen entry button
	def callback2_2(self):
		text = self.entry2.get()
		self.entry2.delete(0, END)
		self.displayText(text, "You", 2)

#class so text boxes are read only by the user and can't be edited
class ReadOnlyText(Text):
	def __init__(self, *args, **kwargs):
		Text.__init__(self, *args, **kwargs)
		self.redirector = WidgetRedirector(self)
		self.insert = self.redirector.register("insert",
			lambda *args, **kw: "break")
		self.delete = self.redirector.register("delete", 
			lambda *args, **kw: "break")