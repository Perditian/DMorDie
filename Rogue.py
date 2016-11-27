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
from math import ceil

LONGWAIT = 15
SHORTWAIT = 10
REALLYSHORTWAIT = 5


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
		#	Window.displayText(name + " has " + str(person.Money) + " zenny", "", 1)
			if name != self.name:
				total_money += person.Money
				if person.Money >= max_money:
					max_money = person.Money
					victim = name
		return (max_money, total_money, victim)

	def success_or_fail(self, Window, prompt = None):
		Window.print_options({'s':'success', 'f':'failure'}, prompt)
		if Window.Event.wait(LONGWAIT) is True:
			Window.Event.clear()
			if Window.command == 's':
				return True
		return False

	def pickpocket(self, game_state, Victim):
		People = game_state.Characters()
		Window = game_state.Window()
		Money_Earned = People[Victim].Money
		Window.displayText("The " + self.name + " creeps up to " + Victim, self.name, 2)
		Window.displayText("The " + self.name + " wants to pickpocket " + Victim, ">", 1)
		if self.Event.wait(SHORTWAIT) is False:
			Window.displayText("The " + self.name + " attempted to pickpocket " + Victim, ">>", 2)
			Window.displayText("And failed miserably. They lost 10gp.", ">>", 2)
			with game_state.Lock():
				People[self.name].Money -= 10
				People[self.name].Money = min(0, People[self.name].Money)
			Window.displayText("The " + self.name + " now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			cmd = self.success_or_fail(Window, "Does the " + self.name + " succeed?")
			if cmd:
				with game_state.Lock():
					Money_Earned = People[Victim].Money
					People[self.name].Money += Money_Earned
					People[Victim].Money = 0
				Window.displayText("The " + self.name + " pickpocketed " + Victim + " for " + str(Money_Earned) + " zenny!!", "", 2)
			else:
				Window.displayText("The " + self.name + " failed!!", "", 2)
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
		if self.Event.wait(SHORTWAIT) is False:
			Money_Earned = 0
			Window.displayText("Oh no! The " + self.name + " got caught stealing :(", "", 2)
			Window.displayText("The " + self.name + " now has " + str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			cmd = self.success_or_fail(Window, "Does the " + self.name + " succeed?")
			if cmd:
				with game_state.Lock():
					Money_Earned = Places[Victim].Hidden_Money
					People[self.name].Money += Money_Earned
					Places[Victim].Hidden_Money = 0
				Window.displayText("The "+self.name+" stole from " + Victim + " for " + str(Money_Earned) + " zenny!!", "", 2)
			else:
				Money_Earned = 0
				Window.displayText("The "+self.name+" failed!!", "", 2)
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
#			Window.displayText(name + " has " + str(place.Hidden_Money) + " hidden zenny", "", 1)
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



	def plead_for_money(self, Window, Person):
		if self.Alignment == "chaotic":
			Window.displayText("Fine, didn't like you much anyway.", self.name, 2)
		else:
			Window.displayText("No! Please! I'm desperate for cash!", self.name, 2)
			Window.displayText("I'll do anything! ANYTHING.", self.name, 2)
			Window.displayText("Urgh, fine. There's a dragon.", Person, 2)
			Window.displayText("Go slay it, and I MIGHT give ye a coin or two.", Person, 2)
			Window.displayText("The " +self.name+" considers the offer...", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		return


	def ask(self, game_state, Person):
		People = game_state.Characters()
		Window = game_state.Window()
		Window.displayText("The "+ self.name +" walks up to " + Person, "<", 2)
		Window.displayText("The "+self.name+" wants to talk to " + Person, "<", 1)
		if self.Event.wait(SHORTWAIT) is False:
			Window.displayText(Person + " ignores the " + self.name, "", 2)
			return (0, game_state)
		self.Event.clear()
		Window.displayText("The "+self.name+" waits for "+Person+" to respond.", "", 2)
		with People[Person].Lock:
			Window.displayText("The "+Person+" turns to the "+self.name, "", 2)
			prompt = "How should " + Person + " greet the " + self.name +"?"
			dic = {"0":"Well Hello there, weary Traveler...", "1":"GAH! A " + self.name + "! Get away from me!!"}
			Window.print_options(dic, prompt)
			if Window.Event.wait(LONGWAIT) is True:
				Window.Event.clear()
				if Window.command == "0":
					Window.displayText("Well Hello there, weary Traveler.", Person, 2)
					Window.displayText("What brings you to this flashy " + Person +"?", Person, 2)

					if self.Alignment == "chaotic":
						Window.displayText("Need some money, bro.", self.name, 2)
						dic0 = "Got gold for ye, but there's a price..."
						extended0 = [(Person, "I got some gold for ye, but"), (Person, "it comes with a price."), \
									(self.name, "...I need to pay for free money?"), (Person, "Aie, not with ye gold," ),(Person, "but with ye body."), \
									(self.name, "WHAT?!"), (Person, "There's a dragon need'n some slay'n."),(Person," You do that, you get me gold."), \
									(self.name, "Oh, that's what you meant..."),(self.name, "I'll consider it.")]
					else:
						Window.displayText("Yo, you got any quests with rewards?", self.name, 2)
						dic0 = "There's a dragon need'n some slay'n"
						extended0 = [(Person, "You in need of quest? Har Har Har!"),(Person," A quest I got for ye."), \
						             (Person, "I heard there's a violent,"),(Person,"vicious dragon haunting the land"), \
						             (Person, "Slay that beast, and I'll give ye my thanks."), \
						             (Person, "..also some gold, I guess."), (self.name, "Many thanks, my good " + Person +", I'll kill it immediately!")]
					prompt = "How should " + Person + " respond?"
					dic.clear()
					dic = {"0":dic0, "1":"You know what? I don't like your attitude."}
					Window.print_options(dic, prompt)
					if Window.Event.wait(LONGWAIT) is True:
						Window.Event.clear()
						if Window.command == "0":
							for (speaker, dialogue) in extended0:
								Window.displayText(dialogue, speaker, 2)
						else:
							Window.displayText("You know what? You're too shady.", Person, 2)
							Window.displayText("I don't deal with sketchy characters.", Person, 2)
							self.plead_for_money(Window, Person)
				else:
					Window.displayText("GAARGHH?!! You foul " + self.name + ".", Person, 2)
					Window.displayText("I have no business with you.", Person, 2)
					self.plead_for_money(Window, Person)
			else:
				Window.displayText(Person + " ignores the " + self.name, "", 2)
		Window.displayText("", "", 2)
		Window.displayText("", "", 2)
		return (0, game_state)


	def ask_utility(self, game_state):
		People = game_state.Characters()
		people_list = People.keys()
		people_list.remove(self.name)
		victim = people_list[random.randint(0, len(people_list) - 1)]
		#return (random.random() * 100, random.random() * 100, victim)
		return (random.randint(0, 1), 1, victim)

