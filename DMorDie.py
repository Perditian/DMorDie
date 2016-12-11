#!/usr/bin/python3
"""
 Avita Sharma, Eric Wyss, David Taus
 DM or DIE!!
 Main game loop
 Uses Python 3
"""

from AI import AI 
from Action import Action
from Rogue import Rogue
from Warrior import Warrior
import threading
import random
from DungeonMaster import DungeonMaster
from GameState import GameState
from postOffice import PostOffice
from Battle import *
import sys
from NPC_and_Location import *

try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *

from math import ceil


def main():
	# Make the Locations and NPCs:    
	Tavern = Location('The Don\'t go Inn', health = 30)
	barkeep = NPC("Anita Colbier", 0)
	barkeep.barkeep = True
	Tavern.Bartender = barkeep
	barkeep.Location = Tavern
	Tavern.Tavern = True
	Tavern.tab = {}

	Village = Location("Rock Bottom Village", 0)
	Village.Village = True
	OldMan = NPC(Home = Village)

	# Make the Playable Characters:
	rogue = Rogue(0, Home = Village)
	rogue1 = Rogue(1, 'Assassin', Village)
	warrior = Warrior(0, Home = Village)
	warrior1 = Warrior(1, Home = Village, name = "Knight")

	# create the main window:
	window = Tk()
	window.geometry("1328x755")
	window.config(bg = "#1a0d00")
	DM = DungeonMaster(window)

	# build the post office:
	boxes = PostOffice()
	#for name in [rogue.name, warrior.name]:
	for name in [rogue.name, rogue1.name, warrior.name, warrior1.name]:
		boxes.add_Name(name)

	# Wrap the above in the Game State:
	game_state = GameState(boxes, {rogue.name:rogue, rogue1.name:rogue1,
								   warrior.name:warrior,warrior1.name:warrior1, 
		                           OldMan.name:OldMan, barkeep.name:barkeep},
		         {Tavern.name:Tavern, Village.name:Village}, DM)

	DM.set_GameState(game_state)

	# Make the Monster:
	num_chars = len(game_state.Characters())
	dagon = Dragon("Menacing Dragon", health = (num_chars * 10))

	# create Playable Character threads:
	Rogue_thread = threading.Thread(target=rogue.life, args=(game_state,))
	Rogue_thread1 = threading.Thread(target=rogue1.life, args=(game_state,))
	Warr_thread = threading.Thread(target=warrior.life, args=(game_state,))
	Warr_thread1 = threading.Thread(target=warrior1.life, args=(game_state,))
	Rogue_thread.start()
	Rogue_thread1.start()
	Warr_thread.start()
	Warr_thread1.start()

	# create the Battle thread:
	battle = Battle()
	Battle_thread = threading.Thread(target=battle.life, args=(dagon,
					# [Rogue_thread, Warr_thread],
		            [Rogue_thread, Rogue_thread1, Warr_thread, Warr_thread1],
		            game_state))
	Battle_thread.start()

	# Start the game!
	# open the main window:
	window.mainloop()
	Battle_thread.join()
	return 

if __name__ == '__main__':
	main()

