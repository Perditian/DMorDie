"""
Warrior Class, extends AI

"""

from AI import AI 
from Action import Action
import threading
import random
from DungeonMaster import DungeonMaster
from GameState import GameState
import sys
from math import ceil
import time




class Warrior(AI):

	def __init__(self, Alignment = 0, name = "Barbarian", Location = None):
		if Alignment is 0:
			self.Alignment = 'chaotic'
			self.anger = 5
			self.drunkeness = 3
		else:
			self.Alignment = 'good'
			self.anger = 3
			self.drunkeness = 5

		Pickpocketing = Action(self.pickpocket, self.pickpocket_utility, 0.6)
		Default = Action(self.default_action, self.default_utility, 1)
		Stealing = Action(self.steal, self.stealing_utility, 0.4)
		Asking = Action(self.ask, self.ask_utility, 1)
		
		Goals = ['Make Money', 'Ask']
		Weights = [0.5, 0.5]
		Actions = {str(0):[Pickpocketing, Stealing], str(1):[Asking]}

		AI.__init__(self, Goals, Weights, Actions, 0.5, Default, name, 20, True, Location)
		self.Money = 100
		self.Hidden_Money = 0
		self.lounge = False
	

	def killing_utility(self, game_state):
		People = game_state.Characters()
		Window = game_state.Window()
		max_health = 0
		total_health = 0
		victim = None
		for (name, person) in People.items():
		#	Window.displayText(name + " has " + str(person.Money) + " zenny", "", 1)
			if name != self.name:
				total_health += person.health
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
			roll = random.randint(0, 20) + self.sleight # simple d20 - sleight of hand
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
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
			roll = random.randint(0, 20) + self.sleight # simple d20 - sleight of hand
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
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
			self.ready2battle.set()
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

		"""
		NOTE: THIS COULD MAKE A DEADLOCK HAPPEN:
		"""
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
							self.ready2battle.set()
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


	def attack(self, finished, Monster, game_state):
		self.Event.clear()
		Window = game_state.Window()
		if self.lounge is True:
			Window.displayText(self.name +" lounges in the back, doing nothing.", "", 2)
			return
		if self.health < 5:
			Window.displayText(self.name + " is breathing heavily; their face is scrunched up, blood drenching their clothes.", "", 2)

		if random.random() < 0.5:
			Window.displayText(self.name + " becomes invisible, inching towards the " + Monster.name + "'s pile of gold.", "", 2)
			Window.displayText(self.name + " wants to steal from the " + Monster.name, "", 1)
			if self.Event.wait(LONGWAIT) is False:
				self.Event.clear()
				Window.displayText(self.name + " tries to do something, fails, and hurts themself.", "", 2)
				self.health -= 2
				return
			self.Event.clear()
			roll = random.randint(0, 20) + self.sleight # simple d20 - sleight of hand
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			dic = {"s":"success", "f":"failure"}
			Window.print_options(dic, prompt)
			if Window.Event.wait(LONGWAIT) is True:
				Window.Event.clear()
				if Window.command is "s":
					Window.displayText(self.name+ " steals 10gp from "+ Monster.name, "", 2)
					Window.displayText("ROAAARRRWR!! Me Gold!! Not me Gold!!", Monster.name, 2)
					Window.displayText(Monster.name+" bites their lip in disgust; their teeth pierce their skin and draw blood.", "", 2)
					with game_state.Lock():
						self.Money += 10
					with Monster.Lock():
						Monster.health -= 10
						if Monster.health <= 0:
							finished.set()
				else:
					if roll > 15:
						Window.displayText(self.name + " glares at the Dungeon Master |:<", "", 1)
					Window.displayText("Swiper no swiping!", Monster.name, 2)
					Window.displayText("Swiper no swiping!", Monster.name, 2)
					Window.displayText("Swiper no swiping!", Monster.name, 2)
					Window.displayText("Oh, man!", self.name, 2)
					Window.displayText(self.name + " failed to steal any gold.", "", 1)
				return
		else:
			Window.displayText(self.name + " wants to talk to the "+ Monster.name, "", 1)
			Window.displayText(self.name + " waltzs up to the " + Monster.name, "", 2)
			if self.Event.wait(LONGWAIT) is False:
				Window.displayText(self.name + " tries to do something, fails, and hurts themself.", "", 2)
				self.health -= 2
				return
			self.Event.clear()
			roll = random.randint(0, 20) + self.persuasion  # simple d20 - persuasion check
			Window.displayText(self.name + " rolled a " + str(roll) + " on their persuasion check.", "", 1)
			prompt = "How does " + Monster.name+ " respond?"
			dic = {"0":"How dare ye! Face my flames instead!", 
			       "1":"Hm...I'll listen to what ye have to say."}
			Window.print_options(dic, prompt)
			if Window.Event.wait(LONGWAIT) is True: 
				Window.Event.clear()
				if Window.command is "0":
					Window.displayText("How dare ye think ye can speak with me!", Monster.name, 2)
					Window.displayText("Face my spit instead, cretein!", Monster.name, 2)
					Window.displayText(Monster.name+" spits fire all over the "+self.name +"!", "", 2)
					self.health -= 3
					return
				elif Window.command is "1":
					Window.displayText("...Ye has 3 mins to say what ye needs to say.", Monster.name, 2)
					if self.Alignment is "chaotic":
						Window.displayText("I'm just here for the money.", self.name, 2)
						Window.displayText("Pay me, and I'll leave you alone.", self.name, 2)
						dic0 = "Here's 100gp to attack the guy next to you."

						victim = None
						People = game_state.Characters()
						for (name, person) in People.items():
							if person.fighter:
								if name != self.name:
									if person.dead is False:
										victim = name
										break
						if victim is not None:
							extended0 = [(Monster.name, "Here's 100 gold to attack " + victim),
							             (self.name, "Ok."), ("", self.name +" throws a knife into " + victim),
							             (victim, "WTH?!?! OW")]
						else:
							extended0 = [(self.name, "...I'm the only one here...right?"), (Monster.name, "Hehehehe...")]
					else:
						Window.displayText("Why, good sir, are you attacking villagers?", self.name, 2)
						dic0 = "None of ye beezwax, busta"
						Who = Monster.name
						extended0 = [(self.name, "But sir! I'm sure we can reach an agreement."), 
						             (Who, "*Sigh*, If ye must know, it's cause I hate'm."),
						             (self.name, "...Why?"), (Who, "They called me names. Foul names. Unspeakable names."),
						             (self.name, "Like 'terriplasty mcdragin on'?"), (Who, "Worse! Like 'Whydoesthisdragonspeak' and 'I'mnotanoldmangoshdarnit'"),
						             (self.name, "Hm, those are some pretty terrible names."), (self.name, "I guess you are justified in your murderous rampage."),
						             (self.name, "Well, then, carry on fine "+Who), (self.name, "I'll just be lounging back there.")]
					prompt = "How does the "+Monster.name+" respond?"
					dic.clear()
					dic = {"0":dic0, "1":"ALL THE FLAMES!!"}
					Window.print_options(dic, prompt)
					if Window.Event.wait(LONGWAIT) is True: 
						Window.Event.clear()
						if Window.command is "0":
							for (name, dia) in extended0:
								Window.displayText(dia, name, 2)
							if self.Alignment is "chaotic":
								self.Money += 100
								if victim is not None:
									People = game_state.Characters()
									with game_state.Lock():
										People[victim].health -= 5
							else:
									self.lounge = True
						else:
							Window.displayText("How dare ye think ye can speak with me!", "Dragon", 2)
							Window.displayText("Face my spit instead, cretein!", "Dragon", 2)
							Window.displayText(Who+" spits fire all over the "+self.name+"!", "", 2)
							self.health -= 3
						return
		Window.displayText(self.name + " tries to do something, fails, and hurts themself.", "", 2)
		self.health -= 2
		return

