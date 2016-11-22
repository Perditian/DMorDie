"""
Rogue Class, extends AI
so far, only a chaotic rogue is defined.

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

class Rogue(AI):

	def __init__(self, Alignment = 'chaotic', name = "Rogue"):
		self.Alignment = Alignment
		
		Pickpocketing = Action(self.pickpocket, self.pickpocket_utility, 0.6)
		Default = Action(self.default_action, self.default_utility, 1)
		Stealing = Action(self.steal, self.stealing_utility, 0.4)
		Asking = Action(self.ask, self.ask_utility, 1)
		
		Goals = ['Make Money', 'Ask']
		Weights = [0.5, 0.5]
		Actions = {str(0):[Pickpocketing, Stealing], str(1):[Asking]}

		AI.__init__(self, Goals, Weights, Actions, 0.5, Default, name)
		self.Money = 0
		self.counter = 0
		self.Hidden_Money = 0


	def pickpocket_utility(self, game_state):
		People = game_state.Characters()
		Window = game_state.Window()
		max_money = 0
		total_money = 0
		victim = None
		for (name, person) in People.items():
			Window.displayText(name + " has " + str(person.Money) + " zenny", "", 1)
			if name != self.name:
				total_money += person.Money
				if person.Money >= max_money:
					max_money = person.Money
					victim = name
		return (max_money, total_money, victim)

	def pickpocket(self, game_state, Victim):
		People = game_state.Characters()
		Window = game_state.Window()
		Money_Earned = People[Victim].Money
		Window.displayText("The " + self.name + " creeps up to " + Victim, self.name, 2)
		Window.displayText("The " + self.name + " wants to pickpocket " + Victim, ">", 1)
		if self.Event.wait(105) is False:
			Window.displayText("The " + self.name + " attempted to pickpocket " + Victim + 
				               "; failed miserably, and lost 10gp.", ">>", 2)
			with game_state.Lock():
				People[self.name].Money -= 10
				People[self.name].Money = min(0, People[self.name].Money)
			Window.displayText("The " + self.name + " now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			with game_state.Lock():
				Money_Earned = People[Victim].Money
				People[self.name].Money += Money_Earned
				People[Victim].Money = 0
			Window.displayText("The " + self.name + " pickpocketed " + Victim + " for " + str(Money_Earned) + " zenny!!", "", 2)
			Window.displayText("The " + self.name + " now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		self.Event.clear()
		return (Money_Earned, game_state)

	# ideally this is for buildings/places, not people:
	def steal(self, game_state, Victim):
		Places = game_state.Locations()
		People = game_state.Characters()
		Window = game_state.Window()
		Window.displayText("The " + self.name +" sneaks up to " + Victim, "<", 2)
		Window.displayText("The "+self.name +" wants to steal from " + Victim, "<", 1)
		if self.Event.wait(105) is False:
			Money_Earned = 0
			Window.displayText("Oh no! The " + self.name + " got caught stealing :(", "", 2)
			Window.displayText("The " + self.name + " now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			with game_state.Lock():
				Money_Earned = Places[Victim].Hidden_Money
				People[self.name].Money += Money_Earned
				Places[Victim].Hidden_Money = 0
			Window.displayText("The "+self.name+" stole from " + Victim + " for " + str(Money_Earned) + " zenny!!", "", 2)
			Window.displayText("The "+self.name+" now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		self.Event.clear()
		return (Money_Earned, game_state)

	def stealing_utility(self, game_state):
		Places = game_state.Locations()
		Window = game_state.Window()
		max_money = 0
		total_money = 0
		victim = None
		for (name, place) in Places.items():
			Window.displayText(name + " has " + str(place.Hidden_Money) + " hidden zenny", "", 1)
			if name != self.name:
				total_money += place.Hidden_Money
				if place.Hidden_Money >= max_money:
					max_money = place.Hidden_Money
					victim = name
		return (max_money, total_money, victim)


	def default_action(self, game_state, N=None):
		MAX_UTILITY = 10000000
		People = game_state.Characters()
		Window = game_state.Window()
		People[self.name].counter += 1
		if People[self.name].counter >= 2:
			Window.displayText(self.name + " went to the dungeon and got eaten by a Troll.", "", 2)
			exit(0)
		Window.displayText("Waiting to go to dungeon...", "", 2)
		game_state.set_Characters(People)
		return (MAX_UTILITY, game_state)

	def default_utility(self, game_state):
		MAX_UTILITY = 10000000
		return (MAX_UTILITY, MAX_UTILITY)


	def ask(self, game_state, Person):
		People = game_state.Characters()
		Window = game_state.Window()
		Window.displayText("The "+ self.name +" walks up to " + Person, "<", 2)
		Window.displayText("The "+self.name+" wants to talk to " + Person, "<", 1)
		
		"""
		if self.Event.wait(205) is True:
			Window.displayText("The "+self.name+" asks " + Person + " for money.", "", 2)
			Window.displayText(Person + " replies, sure here you go!", "", 2)
			with game_state.Lock():
				People[self.name].Money += 100
			Window.displayText("The "+self.name+" now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
			self.Event.clear()
			return (100, game_state)
		else:
			Window.displayText(Person + " replies, GET AWAY YOU MONSTER.", "", 2)
			Window.displayText("The " + self.name + " now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
			self.Event.clear()
		"""
		return (0, game_state)


	def ask_utility(self, game_state):
		People = game_state.Characters()
		people_list = People.keys()
		people_list.remove(self.name)
		victim = people_list[random.randint(0, len(people_list) - 1)]
		#return (random.random() * 100, random.random() * 100, victim)
		return (random.randint(0, 1), 1, victim)

