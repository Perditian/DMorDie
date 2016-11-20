"""
 Avita Sharma
 
 TESTS FOR AI AND ACTIONS

 In Future: game_state should have the state, messaging, and lock
"""

from AI import AI 
from Action import Action
import threading
import random
from DungeonMaster import DungeonMaster
from GameState import GameState
import sys
from Tkinter import *
from math import ceil

def pickpocket_utility(game_state):
	People = game_state.Characters()
	max_money = 0
	total_money = 0
	victim = None
	for (name, person) in People.items():
		(name + " has " + str(person.Money) + " zenny\n")
		if name != 'Rogue':
			total_money += person.Money
			if person.Money >= max_money:
				max_money = person.Money
				victim = name
	return (max_money, total_money, victim)

def pickpocket(game_state, Victim):
	People = game_state.Characters()
	Window = game_state.Window()
	Money_Earned = People[Victim].Money
	People['Rogue'].Money += Money_Earned
	People[Victim].Money = 0
	Window.displayText("The Rogue pickpocketed " + Victim + " for " + str(Money_Earned) + " zenny!!\n", "", 2)
	game_state.set_Characters(People)
	return (Money_Earned, game_state)

# ideally this is for buildings/places, not people:
def steal(game_state, Victim):
	People = game_state.Characters()
	Window = game_state.Window()
	if People['Rogue'].counter <= 0:
		Money_Earned = 0
		People['Rogue'].counter += 1
		Window.displayText("Oh no! The Rogue got caught stealing :(\n", "", 2)
	else:
		Money_Earned = People[Victim].Hidden_Money
		People['Rogue'].Money += Money_Earned
		People[Victim].Hidden_Money = 0
		Window.displayText("The Rogue stole from " + Victim + " for " + str(Money_Earned) + " zenny!!\n", "", 2)
		game_state.set_Characters(People)
	return (Money_Earned, game_state)

def stealing_utility(game_state):
	People = game_state.Characters()
	Window = game_state.Window()
	max_money = 0
	total_money = 0
	victim = None
	for (name, person) in People.items():
		Window.displayText(name + " has " + str(person.Hidden_Money) + " hidden zenny\n", "", 2)
		if name != 'Rogue':
			total_money += person.Hidden_Money
			if person.Hidden_Money >= max_money:
				max_money = person.Hidden_Money
				victim = name
	return (max_money, total_money, victim)


def default_action(game_state, N=None):
	MAX_UTILITY = 10000000
	People = game_state.Characters()
	Window = game_state.Window()
	People['Rogue'].counter += 1
	if People['Rogue'].counter >= 2:
		displayText("I went to the dungeon and got eaten by a Troll.\n", "", 2)
		exit(0)
	displayText("Waiting to go to dungeon...\n", "", 2)
	game_state.set_Characters(People)
	return (MAX_UTILITY, game_state)

def default_utility(game_state):
	MAX_UTILITY = 10000000
	return (MAX_UTILITY, MAX_UTILITY)


def ask(game_state, Person):
	People = game_state.Characters()
	Window = game_state.Window()
	Window.displayText("The Rogue asks " + Person + " for money.", "", 2)
	if random.random() > 0.5:
		Window.displayText(Person + " replies, sure here you go!", "", 2)
		People['Rogue'].Money += 100
		game_state.set_Characters(People)
		return (100, game_state)
	Window.displayText(Person + " replies, GET AWAY YOU MONSTER.", "", 2)
	game_state.set_Characters(People)
	return (0, game_state)


def ask_utility(game_state):
	People = game_state.Characters()
	people_list = People.keys()
	people_list.remove('Rogue')
	victim = people_list[random.randint(0, len(people_list) - 1)]
	return (random.random() * 100, random.random() * 100, victim)

def main():
	OldMan = AI()
	OldMan.name = 'The Old Man'
	OldMan.Money = 100
	OldMan.Hidden_Money = 0

	Tavern = AI()
	Tavern.name = 'The Don\'t go Inn'
	Tavern.Money = 0
	Tavern.Hidden_Money = 150

	Pickpocketing = Action(pickpocket, pickpocket_utility, 0.6)
	Default = Action(default_action, default_utility, 1)
	Stealing = Action(steal, stealing_utility, 0.4)
	Asking = Action(ask, ask_utility, 1)

	Goals = ['Make Money', 'Ask']
	Weights = [0.5, 0.5]
	Actions = {str(0):[Pickpocketing, Stealing], str(1):[Asking]}

	Rogue = AI(Goals, Weights, Actions, 0.5, Default, 'Rogue')
	Rogue.Money = 0
	Rogue.counter = 0
	Rogue.Hidden_Money = 0

	# create the main window:
	window = Tk()
	window.geometry("1400x755")
	DM = DungeonMaster(window)

	game_state = GameState({}, {Rogue.name:Rogue, OldMan.name:OldMan, \
		         Tavern.name:Tavern}, {}, DM)

	# create the Dungeon Master thread:
	DM_thread = threading.Thread(target=DM.life, args=(game_state,))
	DM_thread.start()

	# start the window/game:
	window.mainloop()

	# create an AI thread:
	Rogue_thread = threading.Thread(target=Rogue.life, args=(game_state,))
	Rogue_thread.start()
	Rogue_thread.join()
	DM_thread.join()

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

