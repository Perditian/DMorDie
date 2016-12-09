from tkinter import *
from math import ceil

class Window():

	def __init__(self, master):
		self.numOfLines = 27

		self.frame1 = Frame(master, height = 700, width = 690, bg = "#99ff99")
		self.divider = Frame(master, height = 700, width = 20, bd = 1, 
			relief = RAISED, padx=5, pady=5, bg = "#ccccff")
		self.frame2 = Frame(master, height = 700, width = 690, bg = "#d9ff66")

		self.frame1.grid(row = 0, column = 0)
		self.divider.grid(row = 0, column = 1)
		self.frame2.grid(row = 0, column = 2)

		self.entry1 = Entry(master, width = 121, bg = "#ccccff", font = ("Courier New", 12))
		self.entry1.bind('<Return>', self.callback1_1)
		self.entry1.grid(row = 1, column = 0, columnspan = 3, ipady = 15, sticky = W)

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

	def callback1_1(self, event):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.displayText(text, "You", 1)

	def callback1_2(self):
		text = self.entry1.get()
		self.entry1.delete(0, END)
		self.displayText(text, "You", 1)

	def displayText(self, message, msgFrom, screen):
		if (screen == 1) :
			displayFunction = self.displayText1
		elif (screen == 2):
			displayFunction = self.displayText2
		numLines = ceil((len(msgFrom) + 3 + len(message)) / 50)
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

	def displayText2(self, message):
		for i in range(self.numOfLines-2, 0, -1):
			lineAbove = self.lines2[i-1][1]
			self.lines2[i][1] = lineAbove
			self.lines2[i][0].config(text = lineAbove)
		newText = message
		self.lines2[0][0].config(text = newText)
		self.lines2[0][1] = newText

#root = Tk()
#root.geometry("500x500")
root2 = Tk()
root2.geometry("1332x755")
root2.config(bg = "#d9ff66")

#app = Window(root2)
app2 = Window(root2)

root2.mainloop()

	# def __init__(self, master):
	# 	self.numOfLines = 27

	# 	self.frame1 = Frame(master, height = 700, width = 690, bg = "#99ff99" )
	# 	self.divider = Frame(master, height = 755, width = 20, bd = 1, 
	# 		relief = RAISED, padx=5, pady=5, bg = "#ccccff")
	# 	self.frame2 = Frame(master, height = 700, width = 690, bg = "#d9ff66")

	# 	self.frame1.grid(row = 0, column = 0)
	# 	self.divider.grid(row = 0, column = 1)
	# 	self.frame2.grid(row = 0, column = 2)

	# 	self.placeholder = Frame(self.frame2, width = 690, height = 50, bg = "#d9ff66")
	# 	self.placeholder.grid(row = self.numOfLines+1, column = 0)

	# 	self.entry1 = Entry(self.frame1, width = 57, bg = "#ccccff", font = ("Courier New", 12))
	# 	self.entry1.bind('<Return>', self.callback1_1)
	# 	self.entry1.grid(row = self.numOfLines+1, column = 0, ipady = 15, sticky = N)

	# 	self.entryButton1 = Button(self.frame1, text="submit", width = 15,
	# 		height = 2, command = self.callback1_2, bg = "#ccccff")
	# 	self.entryButton1.grid(row = self.numOfLines+1, column = 1)
		

	# 	self.lines1 = [[Message(self.frame1, width = 600, bg = "#99ff99", font = ("Courier New", 12)), ""] for i in range(self.numOfLines)]
	# 	i = self.numOfLines-1
	# 	for line in self.lines1:
	# 		line[0].grid(row = i, column = 0, sticky = W)
	# 		i -= 1

	# 	self.lines2 = [[Message(self.frame2, width = 600, bg = "#d9ff66", font = ("Courier New", 12)), ""] for i in range(self.numOfLines)]
	# 	i = self.numOfLines-1
	# 	for line in self.lines2:
	# 		line[0].grid(row = i, column = 0, sticky = W)
	# 		i -= 1
	# def callback1_1(self, event):
	# 	text = self.entry1.get()
	# 	self.entry1.delete(0, END)
	# 	self.displayText(text, "You", 1)
	# 	(fun, args) = self.get_command(text)
	# 	if fun == self.interrupt:
	# 			self.interrupt(args)
	# 	if fun == self.print_menu:
	# 			self.print_menu()

	# def callback1_2(self):
	# 	text = self.entry1.get()
	# 	self.entry1.delete(0, END)
	# 	self.displayText(text, "You", 1)
	# 	(fun, args) = self.get_command(text)
	# 	if fun == self.interrupt:
	# 			self.interrupt(args)
	# 	if fun == self.print_menu:
	# 			self.print_menu()

	# def displayText(self, message, msgFrom, screen):
	# 	if (screen == 1) :
	# 		displayFunction = self.displayText1
	# 	elif (screen == 2):
	# 		displayFunction = self.displayText2
	# 	numLines = ceil((len(msgFrom) + 3 + len(message)) / 50)
	# 	indent = " " * (len(msgFrom) + 2)

	# 	line = msgFrom + ": " + message[0:50]
	# 	displayFunction(line)
	# 	for i in range(numLines-3):	 
	# 		line = indent + message[50*(i+1):50*(i+2)]
	# 		displayFunction(line)
	# 	if (numLines > 1):
	# 		line = indent + message[(numLines-1)*50:len(message)]
	# 		displayFunction(line)


	# def displayText1(self, message):#, msgFrom):
	# 	for i in range(self.numOfLines-1, 0, -1):
	# 		lineAbove = self.lines1[i-1][1]
	# 		self.lines1[i][1] = lineAbove
	# 		self.lines1[i][0].config(text = lineAbove)
	# 	newText = message
	# 	self.lines1[0][0].config(text = newText)
	# 	self.lines1[0][1] = newText

	# def callback2_1(self, event):
	# 	text = self.entry2.get()
	# 	self.entry2.delete(0, END)
	# 	self.displayText(text, "You", 2)

	# def callback2_2(self):
	# 	text = self.entry2.get()
	# 	self.entry2.delete(0, END)
	# 	self.displayText(text, "You", 2)

	# def displayText2(self, message):
	# 	for i in range(self.numOfLines-1, 0, -1):
	# 		lineAbove = self.lines2[i-1][1]
	# 		self.lines2[i][1] = lineAbove
	# 		self.lines2[i][0].config(text = lineAbove)
	# 	newText = message
	# 	self.lines2[0][0].config(text = newText)
	# 	self.lines2[0][1] = newText