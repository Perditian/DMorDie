"""
 Avita Sharma
 
 TESTS FOR AI AND ACTIONS

 In Future: game_state should have the state, messaging, and lock
"""

from AI import AI 
from Action import Action
from Rogue import Rogue
import threading
import random
from DungeonMaster import DungeonMaster
from GameState import GameState
from Battle import *
import sys

try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *

from math import ceil

class NPC (AI):
	
	def __init__(self, name = 'The Old Man'):
		AI.__init__(self)
		self.name = name
		self.Money = 100
		self.Hidden_Money = 0


def main():    
	Tavern = AI()
	Tavern.name = 'The Don\'t go Inn'
	Tavern.Money = 0
	Tavern.Hidden_Money = 150

	rogue = Rogue('chaotic')
	rogue1 = Rogue('good', 'Assasin')
	OldMan = NPC()

	# create the main window:
	window = Tk()
	window.geometry("1332x755")
	window.config(bg = "#d9ff66")
	DM = DungeonMaster(window)

	# opening prompt:
	prompt  = "Hi Dungeon Master, welcome to your new campaign!"
	prompt0 = "There are characters for you to interrupt (i). You can"
	prompt1 = "also print (p) a list of characters and actions "
	prompt2 = "if you forget. Spelling counts!"
	prompt3 = "Press any button to start the game."

	DM.displayText(prompt, "", 1)
	DM.displayText(prompt0, "", 1)
	DM.displayText(prompt1, "", 1)
	DM.displayText(prompt2, "", 1)

	game_state = GameState({}, {rogue.name:rogue, rogue1.name:rogue1, OldMan.name:OldMan},
		         {Tavern.name:Tavern}, DM)

	DM.set_GameState(game_state)

	dagon = Dragon("Menacing Dragon")


	# create the Dungeon Master thread:
	#DM_thread = threading.Thread(target=DM.life, args=(game_state,))
	#DM_thread.start()

	# this "ensures" that the window will be open before the threads start
	# writing to it.
	def start_with_delay(thread):
			thread.start()
			return

	# create an AI thread:
	Rogue_thread = threading.Thread(target=rogue.life, args=(game_state,))
	Rouge_delay = threading.Timer(1.0, start_with_delay, [Rogue_thread])
	Rouge_delay.start()
	#Rogue_thread.start()

	Rogue_thread1 = threading.Thread(target=rogue1.life, args=(game_state,))
	Rouge_delay1 = threading.Timer(1.0, start_with_delay, [Rogue_thread1])
	Rouge_delay1.start()
	# Rogue_thread1.start()

	battle = Battle()
	Battle_thread = threading.Thread(target=battle.life, args=(dagon,
		            [Rogue_thread, Rogue_thread1], game_state))
	Battle_thread.start()

	Window_thread = threading.Thread(target=window.mainloop())
	Window_thread.start()

	Battle_thread.join()
	Window_thread.join()
	#Rogue_thread.join()
	#Rogue_thread1.join()

	
	#DM_thread.join()


	# start the window/game:
	
	#root = Tk()
	#root.geometry("500x500")
	#root2 = Tk()
	#root2.geometry("1400x755")

	#app = Window(root2)
	#app2 = Window(root2)

	#root2.mainloop()
	return 


if __name__ == '__main__':
	main()

