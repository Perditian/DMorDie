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
import sys
from Tkinter import *
from math import ceil

class NPC (AI):
	OldMan = AI()
	OldMan.name = 'The Old Man'
	OldMan.Money = 100
	OldMan.Hidden_Money = 0

	
def main():

    
	Tavern = AI()
	Tavern.name = 'The Don\'t go Inn'
	Tavern.Money = 0
	Tavern.Hidden_Money = 150

	rogue = Rogue('chaotic')

	# create the main window:
	window = Tk()
	window.geometry("1332x755")
	window.config(bg = "#d9ff66")
	DM = DungeonMaster(window)

	game_state = GameState({}, {rogue.name:rogue, OldMan.name:OldMan, \
		         Tavern.name:Tavern}, {}, DM)

	# create the Dungeon Master thread:
	DM_thread = threading.Thread(target=DM.life, args=(game_state,))
	DM_thread.start()

	# create an AI thread:
	Rogue_thread = threading.Thread(target=rogue.life, args=(game_state,))
	Rogue_thread.start()

	window.mainloop()

	Rogue_thread.join()
	DM_thread.join()


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

