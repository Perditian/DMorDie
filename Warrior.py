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

	def __init__(self, Alignment = 0, name = "Barbarian", Home = None):
		# anger = fighting ability
		# drunkeness = how drunk am I
		if Alignment is 0:
			self.Alignment = 'chaotic'
			self.anger = 5
			self.drunkeness = 3
			self.flirter = 0 
			drinking_success = 0.4
			kill_success = 0.6 
		else:
			self.Alignment = 'good'
			self.anger = 3
			self.drunkeness = 5
			self.flirter = 3
			drinking_success = 0.6
			kill_success = 0.4

		KillPeople = Action(self.pickpocket, self.pickpocket_utility, kill_success)
		KillPlaces = Action(self.pickpocket, self.pickpocket_utility, kill_success)
		Drinking = Action(self.steal, self.stealing_utility, drinking_success)
		Flirting = Action(self.ask, self.ask_utility, 1)
		
		Goals = ['Kill things', 'Drink', 'Flirt']
		if Alignment is 0:
			Weights = [0.5, 0.1, 0.4]
		else:
			Weights = [0.1, 0.5, 0.4]

		Actions = {str(0):[Pickpocketing, Stealing], str(1):[Asking]}

		AI.__init__(self, Goals, Weights, Actions, 0.5, Default, name, 20, True, Home)
		self.Money = 100
		self.max_health = 20
		self.branded = True

	def success_or_fail(self, Window, prompt = None):
		Window.print_options({'s':'success', 'f':'failure'}, prompt)
		if Window.Event.wait(LONGWAIT) is True:
			Window.Event.clear()
			if Window.command == 's':
				return True
		return False


	# someone is asking me:
	def ask_me(self, game_state, Askername):
		# If I know about the monster, share that information:
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Asker = People[Askername]
		if self.ready2battle.is_set():
			Window.displayText("Yo, I heard there's a dragon. Help me slay it!", self.name, 2)
			Window.displayText("Ok.", Asker.name, 2)
			with game_state.Lock():
				Asker.ready2battle.set()
		# otherwise, tell them to go away:
		else:
			Window.displayText("Man, don't disturb me.", self.name, 2)

		# message to send to Asker:
		sending = self.msg_cmds["ask"]
		msg = ExpiringMessage(self.name, (sending[1]), LONGWAIT)
		PostOffice.send_built_Message(self.name, Asker.name, msg)
		# set the Asker's internal event to signal we sent them a message:
		with game_state.Lock():
			Asker.InternalEvent.set()
		return

	# I am being pickpocketed!
	def pickpocket_me(self, game_state, Perpetrator):
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Money_Lost = self.Money 
		# wait for the DM to interact with this event
		if People[Perpetrator].Event.wait(SHORTWAIT) is False:
			# DM did not interact, do something horrible:
			Window.displayText("The " + Perpetrator + " attempted to pickpocket " + self.name, "", 2)
			Window.displayText("Ha! You lousy " + Perpetrator+".", self.name, 2)
			Window.displayText(Perpetrator+"'s pride is hurt. They lost 1 emotional health.", "", 2)
			Money_Lost = 0
			with game_state.Lock():
				People[Perpetrator].health -= 1
				People[Perpetrator].health = max(0, People[self.name].health)
				Window.displayText("", "", 2)
				Window.displayText("", "", 2)
		else:
			# DM is interacting with this event:
			# add a penalty to Perpetrator's roll because I noticed:
			roll = random.randint(1, 20) - Perpetrator.sleight # simple d20 - sleight of hand
			roll = max(1, roll)
			myroll = random.randint(1, 20) 
			prompt = Perpetrator + " rolled a " + str(roll)+", and "+self.name+ \
			         " rolled a "+ str(myroll)+", does "+Perpetrator+" succeed?"
			cmd = self.success_or_fail(Window, prompt)
			# DM decided that the Perpetrator succeeded:
			if cmd:
				with game_state.Lock():
					People[Perpetrator].Money += Money_Lost
					self.Money = 0
				Window.displayText("The " + Perpetrator + " pickpocketed " + self.name + " for " + str(Money_Earned) + " zenny!!", "", 2)
			# DM decided that the Perpetrator fails:
			else:
				Window.displayText("The " + Perpetrator + " failed!!", "", 2)
				Money_Lost = 0
				Window.displayText("The " + self.name + " now has " + str(People[self.name].Money) + " zenny", "<", 1)
				Window.displayText("", "", 2)
				Window.displayText("", "", 2)
		# clear Perpetrator's event, so the DM can interact with them again:
		People[Perpetrator].Event.clear()
		"""
		WE NEED 2 SEND THE VICTIM A MESSAGE: ("You tried to pickpocket me", MONEY_LOST)
		"""
		# message to send to Victim:
		sending = self.msg_cmds["pickpocket"]
		msg = ExpiringMessage(self.name, (sending[1], Money_Lost), LONGWAIT)
		PostOffice.send_built_Message(self.name, Perpetrator, msg)
		# set the Perpetrator's internal event to signal we sent them a message:
		People[Perpetrator].InternalEvent.set()
		return



	def killpeople_utility(self, game_state):
		People = game_state.Characters()
		Window = game_state.Window()
		max_health = 0
		total_health = 0
		victim = None
		for (name, person) in People.items():
		#	Window.displayText(name + " has " + str(person.Money) + " zenny", "", 1)
			if name != self.name:
				total_health += person.health
				if person.health >= max_health:
					max_health = person.health
					victim = name

		return (max_health, total_health, victim)

	def killplaces_utility(self, game_state):
		Locations = game_state.Locations()
		Window = game_state.Window()
		max_health = 0
		total_health = 0
		victim = None
		for (name, place) in Locations.items():
		#	Window.displayText(name + " has " + str(person.Money) + " zenny", "", 1)
			if name != self.name:
				total_health += place.health
				if person.health >= max_health:
					max_health = place.health
					victim = name
		return (max_health, total_health, victim)


	def killpeople(self, game_state, Victim):
		People = game_state.Characters()
		Window = game_state.Window()
		health_taken = 0
		if self.Alignment is 'chaotic':
			Window.displayText("Hey! "+ Victim +"! You lookin' at me funny?", self.name, 2)
			Window.displayText("Uh..no? Maybe? Whats it to ya if I did?", Victim, 2)
			Window.displayText("I don't take too kindly to rude folk. In fact, I think it's a public service if I eliminated all of them.", self.name, 2)
		else:			
			Window.displayText(self.name+", you're village called. They want their idiot back", Victim, 2)
			Window.displayText(Victim+ ", you insulted me! I must duel to regain my honor!", self.name, 2)
		if self.drunkeness >= 10:
				Window.displayText("Yo, you're drunk, you need to calm down.", Victim, 2)
				Window.displayText("I'm not drunk *hic*, YOU'RE drunk! Enough talk, fight me!", self.name, 2)
		if self.zombie:
			Window.displayText("Dude, you stink and your face is fallin off", Victim, 2)
			Window.displayText("ITS CAUSE IMMA ZOMBAE GHHHRRRR", self.name, 2)

		Window.displayText("The " + self.name + " wants to attack " + Victim, "", 1)
		if self.Event.wait(SHORTWAIT) is False:
			self.Event.clear()
			if self.drunkeness >= 10:
				Window.displayText(self.name + " swings their fist at "+Victim+", but hit themself instead!", "", 2)
			else:
				Window.displayText("The " + self.name + " swings their axe at " + Victim + ", but ends up hitting themself instead.", ">>", 2)
			Window.displayText("Ha! Why you be hittin yourself?", Victim, 2)
			Window.displayText(self.name +" lost 1 health.", "", 1)
			with game_state.Lock():
				People[self.name].health -= 1
				if not self.zombie:
					People[self.name].health = max(0, People[self.name].health)
					if self.health <= 0:
						self.dead = True
						Window.displayText(self.name + " has killed themself.", "", 2)	
						Window.displayText("The villagers dig a hole in the ground, and bury the "+self.name+"'s corpse.", "", 2)
						Window.displayText("Three days go by...", "", 2)
						Window.displayText("In the dead of night, the ground grinds its teeth. The sky shrieks.", "", 2)
						Window.displayText("A hand bursts from the grave, and crawls itself out. A foot, torso, and body follow.", "", 2)
						Window.displayText("The parts assemble themselves into the " + self.name+"!", "", 2)
						Window.displayText("The "+self.name+" is now a zombie.", "", 2)
						self.zombie     = True
						self.drunkeness = 100
						self.anger      = 100
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
			health_taken = -1
		else:
			roll = random.randint(0, 20) + self.anger # simple d20 - hit roll
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				roll = random.randint(0, 12) + self.anger # simple d12 - hit roll
				with game_state.Lock():
					People[Victim].health -= roll
					People[Victim].health = max(1, People[self.name].health)
				if self.zombie:
					Window.displayText("The undead " + self.name + "lunges out and bites "+ Victim+", dealing "+str(roll)+" damage!!", "", 2)
				elif self.drunkeness >= 10:
					Window.displayText(self.name+" spazes towards "+Victim+", seems to lunge sideways, but kicks upwards, sending "+Victim+" flying!!", "", 2)
				else:
					Window.displayText("The " + self.name + " swings their axe at " + Victim + " and deals " + str(roll) + " damage!!", "", 2)
				health_taken = roll
			else:
				Window.displayText("The " + self.name + " swings their axe and misses!!", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		self.Event.clear()
		self.drunkeness -= 1
		self.drunkeness = max(0, self.drunkeness)
		return (health_taken, game_state)

	# ideally this is for buildings/places, not people:
	def killplaces(self, game_state, Victim):
		Places = game_state.Locations()
		People = game_state.Characters()
		Window = game_state.Window()
		destroyed = 0
		Window.displayText("The " + self.name +" sees an Ogre in the" + Victim, "", 2)
		Window.displayText("The "+self.name +" wants to attack the Ogre!", "", 1)
		if self.Event.wait(SHORTWAIT) is False:
			self.Event.clear()
			Window.displayText(self.name + " slahes and thrashes against the infernal Ogre", "", 2)
			Window.displayText("But the Ogre is really a Windmill!", "", 2)
			Window.displayText(Victim +" now has one less Windmill", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			self.Event.clear()
			roll = random.randint(0, 20) + self.anger # simple d20 - sleight of hand
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				roll = random.randint(0, 12) + self.anger # simple d12 - sleight of hand
				if self.drunkeness >= 10:
					Window.displayText(self.name + " sees a Windmill in the distance, and becomes enraged", "", 2)
					Window.displayText("WINDMILL YOU SHALL CURSE MY FAMILY'S NAME NO LONGER!", self.name, 2)
					Window.displayText(self.name + " ignores the Ogre, and destroys the Windmill instead.", "", 2)
				else:
					with game_state.Lock():
						Window.displayText("Argh! Why do you hurt me so?", "Ogre", 2)
						Window.displayText("Devilish creature! your existence is a bane in this universe.", self.name, 2)
						Window.displayText("Begone!", self.name, 2)
						Window.displayText(self.name+" slashes and pierces the Ogre. The Ogre slams and rushes "+self.name+" but slips, and is impaled. The Ogre is no more.", "", 2)

						Places[Victim].health -= roll
						if Places[Victim].health <= (Places[Victim].max_health * 0.5):
							Window.displayText(Victim +" has a reputation for being unkind to Ogre-kind. No Ogre comes there anymore.", "", 2)
							Window.displayText(Victim+"'s GDP takes a hit from the loss of the Ogres. People are starving in the streets.", "", 2)
							Window.displayText("The villagers glare at the "+self.name+", refusing to sell them anything anymore in retaliation.", "", 2)
							Victim.branded.append(self.name)
			else:
				Window.displayText(self.name + " slahes and thrashes against the infernal Ogre", "", 2)
				Window.displayText("But the Ogre is really a Windmill!", "", 1)
				Window.displayText(Victim +" now has one less Windmill", "", 1)
			self.Event.clear()
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
			self.drunkeness -= 1
			self.drunkeness = max(0, self.drunkeness)
		return (Money_Earned, game_state)

	def drinking_utility(self, game_state):
		Locations = GameState.Locations()
		bar = None
		for (name, place) in Locations:
			try:
   				 if self.name is not in place.branded:
					bar = name
			except AttributeError:
    			pass
		return (self.max_health - self.health, bar)


	def drinking(self, game_state, Tavern):
		Places = game_state.Locations()
		People = game_state.Characters()
		Window = game_state.Window()

		Window.displayText(self.name + " is in the Tavern", "", 2)
		Window.displayText(Tavern.barkeep.name+", gimme another!", self.name, 2)
		with game_state.Lock():
			if self.Money > 0:
				Window.displayText(self.name+" shines a gold piece, and slams it on the table.", "", 2)
				self.Money -= 1
				self.health += math.ceil((self.max_health - self.health) * 0.1) # gain 10% of what you need
				self.health = min(self.max_health, self.health)
			else:
				Window.displayText("I need a coin, for a drink.", Tavern.barkeep.name, 2)
				Window.displayText("Put'er on my tab.", self.name, 2)
				Tavern.tab[self.name] = Tavern.tab.get(self.name, 0) + 1
				self.health += math.ceil((self.max_health - self.health) * 0.1) # gain 10% of what you need
				self.health = min(self.max_health, self.health)
				if Tavern.tab[self.name] >= 5:
					Window.displayText("Dude, if ya keep drinkin without payin, I'mma hafta kick you out permanently.", Tavern.barkeep.name)
				if Tavern.tab[self.name] >= 10:
					Window.displayText("Thats enough! Pay me at once or geddout.", Tavern.barkeep.name, 2)
					Window.displayText(self.name + " has no money, and was thrown out.", "", 2)
					Tavern.branded.append(self.name)
					return
		Window.displayText("Oie! Half-Orc! Betcha can't drink as much as I!", self.name, 2)
		Window.displayText("Gahahaha! Mangy mortal, your puny stomach can't even contain one of my tankards.", "Imanorc", 2)
		Window.displayText("You're on! *glug* *glug* *chug* *glug* *glug*", self.name, 2)
		Window.displayText("Issat all you got? *gloug* *gloug* *choug* *gloug* *gloug*", "Imanorc", 2)
		Window.displayText("After almost clearing the "+Tavern.name+", ", "", 2)
		Window.displayText("*Hic* Howwabout we armwrestle an whoever wins picksupthe tab?", self.name, 2)
		Window.displayText("Arright, pun-*hic*-y warrior.", "Imanorc", 2)
		Window.displayText(self.name + " wants to armwrestle Imanorc", "", 1)
		if self.Event.wait(SHORTWAIT) is False:
			self.Event.clear()
			Window.displayText("Grrrrghhh!!!! Why you so strronng???", self.name, 2)
			Window.displayText("Gahahaha! Weakling.", "Imanorc", 2)
			Window.displayText("Imanorc crushes "+self.name+"'s hand for fun.", "", 2)
			with game_state.Lock():
				self.health -= 5
				self.health = max(0, self.health)
				self.money -= 5
				self.money = max(0, self.money)
		else:
			self.Event.clear()
			roll = random.randint(0, 20) + self.drunkeness # simple d20 - athletics
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
					Window.displayText("*BANG* Ha! I Win!!", self.name, 2)
					Window.displayText("Nooo!! How could this be!", "Imanorc", 2)
					with game_state.Lock():
						self.money  += 5
						self.health += math.ceil((self.max_health - self.health) * 0.1)
						self.health = min(self.max_health, self.health)
						self.drunkeness += 5
			else:
				Window.displayText("Grrrrghhh!!!! Why you so strronng???", self.name, 2)
				Window.displayText("Gahahaha! You're so weak.", "Imanorc", 2)
				Window.displayText(self.name+"'s arm is strained.", "", 2)
				with game_state.Lock():
					self.health -= 1
					self.health = max(0, self.health)
					self.money -= 5
					self.money = max(0, self.money)
		return


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


	def flirt(self, game_state, Person):
		People = game_state.Characters()
		Window = game_state.Window()
		Window.displayText("The "+ self.name +" saunters up to " + Person, "", 2)
		Window.displayText("The "+self.name+" wants to flirt with " + Person, "", 1)
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
			
			if self.Alignment is "
			
			
			
			
			Window.displayText()
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


	def flirt_utility(self, game_state):
		People = game_state.Characters()
		people_list = People.keys()
		people_list.remove(self.name)
		victim = people_list[random.randint(0, len(people_list) - 1)]
		try:
   			if People[victim].barkeep:
   				return(1000, 1000, victim)
		except AttributeError:
			return (random.randint(0, 10), 10, victim)


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

