"""
Avita Sharma, Eric Wyss, Davis Taus
Warrior Class, extends AI

Warriors can:
	(*) Attack other characters
	(*) Attack other locations
	(*) Drink in the Tavern
	(*) Flirt with other characters
	(*) Attack monsters in battle

Avita Sharma, Eric Wyss, David Taus
"""

from AI import AI 
from Action import Action
import threading
import random
from DungeonMaster import DungeonMaster
from GameState import *
import sys
from math import ceil
from expiringObject import ExpiringMessage
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

		KillPeople = Action(self.killpeople, self.killpeople_utility, 
			                kill_success)
		KillPlaces = Action(self.killplaces, self.killplaces_utility, 
			                kill_success)
		Drinking = Action(self.drinking, self.drinking_utility, 
						  drinking_success)
		Flirting = Action(self.flirt, self.flirt_utility, 1)
		
		Goals = ['Kill things', 'Drink', 'Flirt']
		if Alignment is 0:
			Weights = [0.5, 0.1, 0.4]
		else:
			Weights = [0.1, 0.5, 0.4]

		Actions = {str(0):[KillPeople, KillPlaces], str(1):[Drinking], 
				   str(2):[Flirting]}

		AI.__init__(self, Goals, Weights, Actions, 0.5, name, 20, True, Home)
		self.Money = 100
		self.max_health = 20
		self.branded = True
		self.flirted_with = []
		self.shambles = 0

	# ask the DM if we succeed or fail:
	def success_or_fail(self, Window, prompt = None):
		Window.print_options({'s':'success', 'f':'failure'}, prompt)
		if Window.Event.wait(LONGWAIT) is True:
			Window.Event.clear()
			if Window.command == 's':
				return True
		return False


	# someone is asking me:
	def ask_me(self, game_state, Askername):
		self.Event.clear()
		# If I know about the monster, share that information:
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Asker = People[Askername]
		if self.ready2battle.is_set():
			Window.displayText("Yo, I heard there's a dragon. "\
				               "Go with me to slay the beast!", self.name, 2)
			Window.displayText("...Fine.", Asker.name, 2)
			game_state.withLock(lambda:Asker.ready2battle.set())
		# otherwise, tell them to go away:
		else:
			Window.displayText("Man, don't disturb me.", self.name, 2)

		# message to send to Asker:
		sending = self.msg_cmds["ask"]
		msg = ExpiringMessage(self.name, (sending[1]), LONGWAIT)
		PostOffice.send_built_Message(self.name, Asker.name, msg)
		# set the Asker's internal event to signal we sent them a message:
		game_state.withLock(lambda:Asker.InternalEvent.set())
		return


	# I am being pickpocketed!
	def pickpocket_me(self, game_state, Perpetrator):
		self.Event.clear()
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Money_Lost = self.Money 
		game_state.withLock(lambda:People[Perpetrator].Event.clear())
		# wait for the DM to interact with this event
		if People[Perpetrator].Event.wait(SHORTWAIT) is False:
			# DM did not interact, do something horrible:
			Window.displayText("The " + Perpetrator +\
			                   " attempted to pickpocket " + self.name, "<", 2)
			Window.displayText("Ha! You lousy " + Perpetrator+".", 
				               self.name, 2)
			Window.displayText(Perpetrator+"'s pride is hurt. "\
				               "They lost 1 emotional health.", "<", 2)
			Money_Lost = 0
			def pickhealth():
				if People[Perpetrator].health == 1:
					Window.displayText(Perpetrator + " believes in themself, "\
						               "and regains their pride!", "<", 2)
					People[Perpetrator].health += 1
				else:
					People[Perpetrator].health -= 1
					People[Perpetrator].health = \
					                           max(1, People[self.name].health)
				Window.displayText("", "", 2)
				Window.displayText("", "", 2)
			game_state.withLock(pickhealth)
		else:
			# DM is interacting with this event:
			# add a penalty to Perpetrator's roll because I noticed:
			roll = random.randint(1, 20) - Perpetrator.sleight # simple d20 
			roll = max(1, roll)
			myroll = random.randint(1, 20) 
			prompt = Perpetrator + " rolled a " + str(roll)+", and "+\
					self.name+" rolled a "+ str(myroll)+", does "+\
					Perpetrator+" succeed?"
			cmd = self.success_or_fail(Window, prompt)
			# DM decided that the Perpetrator succeeded:
			if cmd:
				def picklost():
					People[Perpetrator].Money += Money_Lost
					self.Money = 0
				game_state.withLock(picklost)
				Window.displayText("The " + Perpetrator + " pickpocketed " +\
				                   self.name + " for " + str(Money_Lost) +\
				                   " zenny!!", "<", 2)
			# DM decided that the Perpetrator fails:
			else:
				Window.displayText("The " + Perpetrator + " failed!!", "<", 2)
				Money_Lost = 0
				Window.displayText("The " + self.name + " now has " + \
					               str(People[self.name].Money) + " zenny", 
					               "<", 1)
				Window.displayText("", "", 2)
				Window.displayText("", "", 2)
		# clear Perpetrator's event, so the DM can interact with them again:
		People[Perpetrator].Event.clear()
		"""
		WE NEED 2 SEND THE VICTIM A MESSAGE: 
		("You tried to pickpocket me", MONEY_LOST)
		"""
		# message to send to Victim:
		sending = self.msg_cmds["pickpocket"]
		msg = ExpiringMessage(self.name, (sending[1], Money_Lost), LONGWAIT)
		PostOffice.send_built_Message(self.name, Perpetrator, msg)
		# set the Perpetrator's internal event to signal
		# we sent them a message:
		game_state.withLock(lambda:People[Perpetrator].InternalEvent.set())
		return

	# utility function for killing people:
	def killpeople_utility(self, game_state):
		People = game_state.Characters()
		Window = game_state.Window()
		max_health = 0
		total_health = 0
		victim = None
		for (name, person) in People.items():
			if name != self.name:
				total_health += person.health
				if person.health >= max_health:
					max_health = person.health
					victim = name

		return (max_health, total_health, victim)

	# utility function for killing things:
	def killplaces_utility(self, game_state):
		Locations = game_state.Locations()
		Window = game_state.Window()
		max_health = 0
		total_health = 0
		victim = None
		for (name, place) in Locations.items():
			total_health += place.health
			if place.health >= max_health:
				max_health = place.health
				victim = name
		return (max_health, total_health, victim)

	# check if I can turn into a zombie, and if so zombify me!
	def zombified(self, Window):
		if not self.zombie:
			self.health = max(0, self.health)
			if self.health <= 0:
				self.dead = True
				Window.displayText(self.name + " has killed themself.", 
								  ">>", 2)	
				Window.displayText("The villagers dig a hole in the "\
								   "ground, and bury the "+self.name+\
								   "'s corpse.", ">>", 2)
				Window.displayText("Three days go by...", ">>", 2)
				Window.displayText("In the dead of night, the ground grinds "\
								   "its teeth. The sky shrieks.", ">>", 2)
				Window.displayText("A hand bursts from the grave, and crawls "\
								   "itself out. A foot, torso, and body "\
								   "follow.", ">>", 2)
				Window.displayText("The parts assemble themselves into the " +\
								   self.name+"!", ">>", 2)
				Window.displayText("The "+self.name+" is now a zombie.", 
								   ">>", 2)
				self.zombie     = True
				self.drunkeness = 100
				self.anger      = 100
		return

	# I kill another fighter:
	def kill_fighter(self, game_state, Victim):
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		health_taken = People[Victim].health
		# message to send to Victim:
		sending = self.msg_cmds["kill"]
		msg = ExpiringMessage(self.name, (sending[0], self.name), LONGWAIT)
		PostOffice.send_built_Message(self.name, Victim, msg)
		msg.clear()
		if msg.read == True:
			self.InternalEvent.wait()
			#  get mail from victim
			mail_from = PostOffice.get_Mail_From(Victim, self.name)
			received = sending[1]
			for msg in mail_from:
				if msg.content[0] == received:
					return (True, msg.content[1], game_state)
			return (True, None, game_state) # just in case 

		return (False, None, None)

	# someone is killing me!
	def kill_me(self, game_state, Perpname):
		self.Event.clear()
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Perpetrator = People[Perpname]
		health_taken = 0
		if Perpetrator.Alignment is 'chaotic':
			Window.displayText("Hey! "+ self.name +"! You lookin' at me "\
				               "funny?", Perpname, 2)
			Window.displayText("Uh...no? Maybe? Whats it to ya if I did?",
			                   Perpname, 2)
			Window.displayText("I don't take too kindly to rude folk. "\
							   "In fact, I think it's a public service if I "\
							   "eliminated all of them.", Perpname, 2)
		else:			
			Window.displayText(Perpname+", your village called. They want "\
							   "their idiot back", self.name, 2)
			Window.displayText(self.name+ ", you've insulted me! I must duel "\
							   "to regain my honor!", Perpname, 2)
		if Perpetrator.drunkeness >= 10:
				Window.displayText("Yo, you're drunk, you need to calm down.", 
								   self.name, 2)
				Window.displayText("I'm not drunk *hic*, YOU'RE drunk! "\
								   "Enough talk, fight me!", Perpname, 2)
		if Perpetrator.zombie:
			Window.displayText("Dude, you stink and your face is fallin off",
							   self.name, 2)
			Window.displayText("ITS CAUSE IMMA ZOMBAE GHHHRRRR", Perpname, 2)

		Window.displayText("The " + Perpname + " wants to attack " + self.name,
						   ">", 1)
		if Perpetrator.Event.wait(SHORTWAIT) is False:
			Perpetrator.Event.clear()
			Attacker = Perpname
			Victim = self.name
			if Perpetrator.drunkeness >= 10:
				Window.displayText(Attacker + " swings their fist at "+\
								   Victim+", but hits themself instead!", 
								   "", 2)
				Window.displayText("Ohhggrr...These stars are pretty pretty"\
								   " *hic* things.", Attacker, 2)
			else:
				Window.displayText("The " + Attacker + " swings their axe at "\
								   + Victim + ", but ends up hitting themself"\
								   " instead.", "", 2)
			Window.displayText("Ha! Why you be hittin yourself?", Victim, 2)
			Window.displayText(Attacker +" lost 5 health.", "<", 1)
			def lost():
				Perpetrator.health -= 5
				Perpetrator.zombified(Window)
			game_state.withLock(lost)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
			health_taken = 5
		else:
			Attacker = Perpname
			Victim = self.name
			# simple d20 - hit roll, penalized since I noticed:
			roll = random.randint(0, 20) - self.anger 
			prompt = Perpname + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				# simple d12 - hit roll
				roll = random.randint(0, 12) + Perpetrator.anger 
				def hit():
					self.health -= roll
					self.health = max(1, self.health)
				game_state.withLock(hit)
				if Perpetrator.zombie:
					Window.displayText("The undead " + Attacker + \
						               "lunges out and bites "+ Victim+\
						               ", dealing "+str(roll)+" damage!!",
						               "", 2)
				elif Perpetrator.drunkeness >= 10:
					Window.displayText(Attacker+" spazes towards "+Victim+\
						               ", seems to lunge sideways, but kicks "\
						               "upwards, sending "+Victim+" flying!!",
						               "", 2)
				else:
					Window.displayText("The " + Attacker + " swings their "\
						               "axe at " + Victim + " and deals " +\
						               str(roll) + " damage!!", "", 2)
				health_taken = roll
			else:
				Attacker = Perpname
				Window.displayText("The " + Attacker + " swings their "\
					               "axe and misses!!", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		def end_fight():
			Perpetrator.Event.clear()
			Perpetrator.drunkeness -= 1
			Perpetrator.drunkeness = max(0, self.drunkeness)
		game_state.withLock(end_fight)

		"""
		WE NEED 2 SEND THE VICTIM A MESSAGE: 
		("You tried to kill me", HEALTH_LOST)
		"""
		# message to send to Victim:
		sending = self.msg_cmds["kill"]
		msg = ExpiringMessage(self.name, (sending[1], health_taken), LONGWAIT)
		PostOffice.send_built_Message(self.name, Perpname, msg)
		# set the Perpetrator's internal event to signal 
		# we sent them a message:
		game_state.withLock(lambda:Perpetrator.InternalEvent.set())
		return (health_taken, game_state)


	def killpeople(self, game_state, Victim):
		self.Event.clear()
		People = game_state.Characters()
		Window = game_state.Window()
		health_taken = 0

		# if the Victim is a fighter, they can fight back:
		if People[Victim].fighter == True: 
			read = False
			(read, rate, new_game_state) = \
									self.kill_fighter(game_state, Victim)
			self.Event.clear()
			if read == True:
				return (rate, new_game_state)
			else:
				return (None, game_state)

		if self.Alignment is 'chaotic':
			Window.displayText("Hey! "+ Victim +"! You lookin' "\
							   "at me funny?", self.name, 2)
			Window.displayText("Uh...no? Maybe? Whats it to ya if I did?", 
							   Victim, 2)
			Window.displayText("I don't take too kindly to rude folk. In "\
							   "fact, I think it's a public service if I "\
							   "eliminated all of them.", self.name, 2)
		else:			
			Window.displayText(self.name+", your village called. They want "\
							   "their idiot back", Victim, 2)
			Window.displayText(Victim+ ", you've insulted me! I must duel to"\
							  " regain my honor!", self.name, 2)
		if self.drunkeness >= 10:
				Window.displayText("Yo, you're drunk, you need to calm down.",
								   Victim, 2)
				Window.displayText("I'm not drunk *hic*, YOU'RE drunk! Enough"\
								   " talk, fight me!", self.name, 2)
		if self.zombie:
			Window.displayText("Dude, you stink and your face is fallin off",
							   Victim, 2)
			Window.displayText("ITS CAUSE IMMA ZOMBAE GHHHRRRR", self.name, 2)

		Window.displayText("The " + self.name + " wants to attack " + \
						   Victim, "", 1)
		if self.Event.wait(SHORTWAIT) is False:
			self.Event.clear()
			Attacker = self.name
			if self.drunkeness >= 10:
				Window.displayText(Attacker + " swings their fist at "+Victim+\
								   ", but hits themself instead!", "", 2)
				Window.displayText("Ohhggrr...These stars are pretty pretty"\
								   " *hic* things.", Attacker, 2)
			else:
				Window.displayText("The " + Attacker + " swings their axe at "\
								   + Victim + ", but ends up hitting themself"\
								   " instead.", "", 2)
			Window.displayText("Ha! Why you be hittin yourself?", Victim, 2)
			Window.displayText(Attacker +" lost 5 health.", "", 1)
			def losthealth():
				People[Attacker].health -= 5
				People[Attacker].zombified(Window)
			game_state.withLock(losthealth)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
			health_taken = 5
		else:
			roll = random.randint(0, 20) + self.anger # simple d20 - hit roll
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				# simple d12 - damage roll
				roll = random.randint(0, 12) + self.anger 
				with game_state.Lock():
					People[Victim].health -= roll
					People[Victim].health = max(1, People[Victim].health)
				if People[Attacker].zombie:
					Window.displayText("The undead " + Attacker + \
									   "lunges out and bites "+ Victim+\
									   ", dealing "+str(roll)+" damage!!", 
									   "", 2)
				elif People[Attacker].drunkeness >= 10:
					Window.displayText(Attacker+" spazes towards "+Victim+\
									   ", seems to lunge sideways, but kicks"\
									   " upwards, sending "+Victim+" flying!!",
									   "", 2)
				else:
					Window.displayText("The " + Attacker + " swings their "\
									   "axe at " + Victim + " and deals " +\
									   str(roll) + " damage!!", "", 2)
				health_taken = roll
			else:
				Window.displayText("The " + Attacker + " swings their axe"\
								   " and misses!!", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		def endkill():
			self.Event.clear()
			self.drunkeness -= 1
			self.drunkeness = max(0, self.drunkeness)
		game_state.withLock(endkill)
		return (health_taken, game_state)

	# kill an ogre:
	def killplaces(self, game_state, Victim):
		self.Event.clear()
		Places = game_state.Locations()
		People = game_state.Characters()
		Window = game_state.Window()
		destroyed = 0
		Window.displayText("The " + self.name +" sees an Ogre in the " +\
						   Victim, "", 2)
		Window.displayText("The "+self.name +" wants to attack the Ogre!",
						   "", 1)
		if self.Event.wait(SHORTWAIT) is False:
			self.Event.clear()
			Window.displayText(self.name + " slahes and thrashes against"\
							   " the infernal Ogre", "", 2)
			Window.displayText("But the Ogre is really a Windmill!", "", 2)
			Window.displayText(Victim +" now has one less Windmill", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			self.Event.clear()
			roll = random.randint(0, 20) + self.anger # simple d20 - hit
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				roll = random.randint(0, 12) + self.anger # simple d12 - damage
				if self.drunkeness >= 10:
					Window.displayText(self.name + " sees a Windmill in the"\
									   " distance, and becomes enraged", ">>", 2)
					Window.displayText("WINDMILL YOU SHALL CURSE MY FAMILY'S"\
									   " NAME NO LONGER!", self.name, 2)
					Window.displayText(self.name + " ignores the Ogre, and "\
									  "destroys the Windmill instead.", ">>", 2)
					Window.displayText(Victim +" now has one less Windmill",
									   "<", 2)
				else:
					with game_state.Lock():
						Window.displayText("Argh! Why do you hurt me so?", 
										   "Ogre", 2)
						Window.displayText("Devilish creature! your existence"\
										   " is a bane in this universe.", 
										   self.name, 2)
						Window.displayText("Begone!", self.name, 2)
						Window.displayText(self.name+" slashes and pierces "\
										  "the Ogre, dealing "+str(roll)+\
										  " damage."\
										  " The Ogre slams and "\
										  "rushes "+self.name+" but slips, "\
										  "and is impaled. The Ogre is no "\
										  "more.", "<", 2)
						destroyed = roll
						def kill_ogre():
							Places[Victim].health -= roll
						game_state.withLock(kill_ogre)
						if Places[Victim].health <= 0:
							Window.displayText(Victim +" has a reputation for"\
											   " being unkind to Ogre-kind. "\
											   "No Ogre comes there anymore.",
											    ">>", 2)
							Window.displayText(Victim+"'s GDP takes a hit "\
											   "from the loss of the Ogres. "\
											   "People are starving in the "\
											   "streets.", ">>", 2)
							Window.displayText("The villagers glare at the "+\
											   self.name+", refusing to sell "\
											   "them anything anymore in "\
											   "retaliation.", ">>", 2)
							game_state.withLock(lambda: \
							          Places[Victim].branded.append(self.name))
			else:
				Window.displayText(self.name + " slahes and thrashes against "\
								   "the infernal Ogre", "<", 2)
				Window.displayText("But the Ogre is really a Windmill!", "<", 2)
				roll = random.randint(1, 12)
				destroyed = roll
				Window.displayText("The Windmill deals "+ str(roll) +\
								   " damage to "+ self.name, "<", 1)
				self.zombified(Window)
		Window.displayText("", "", 2)
		Window.displayText("", "", 2)
		def endkillthings():
			self.Event.clear()
			self.drunkeness -= 1
			self.drunkeness = max(0, self.drunkeness)
		game_state.withLock(endkillthings)
		return (destroyed, game_state)


	# utility function for drinking:
	def drinking_utility(self, game_state):
		Locations = game_state.Locations()
		bar = None
		for (name, place) in Locations.items():
			try:
   				if not self.name in place.branded:
   				 	bar = name
			except AttributeError:
				pass
		return (self.max_health - self.health, self.max_health, bar)

	# drinking at the tavern:
	def drinking(self, game_state, Tavernname):
		self.Event.clear()
		Places = game_state.Locations()
		People = game_state.Characters()
		Window = game_state.Window()
		health = 0
		Tavern = Places[Tavernname]
		Window.displayText(self.name + " is in the Tavern", "", 2)
		Window.displayText(Tavern.Bartender.name+", gimme another!", 
						   self.name, 2)
		with game_state.Lock():
			if self.Money > 0:
				Window.displayText(self.name+" shines a gold piece, and "\
					 			   "slams it on the table.", "", 2)
				def drunkonce():
					self.Money -= 1
					health = math.ceil((self.max_health - self.health) * 0.1)
					self.health += health # gain 10% of what you need
					self.health = min(self.max_health, self.health)
				game_state.withLock(drunkonce)
			else:
				Window.displayText("I need a coin, for some cold beer.", 
								   Tavern.Bartender.name, 2)
				Window.displayText("Put'er on my tab.", self.name, 2)
				def tab():
					Tavern.tab[self.name] = Tavern.tab.get(self.name, 0) + 1
					health = math.ceil((self.max_health - self.health) * 0.1)
					self.health += health # gain 10% of what you need
					self.health = min(self.max_health, self.health)
					if Tavern.tab[self.name] >= 5:
						Window.displayText("Dude, if ya keep drinkin without "\
										   "payin, I'mma hafta kick you out "\
										   "permanently.", 
										   Tavern.Bartender.name)
					if Tavern.tab[self.name] >= 10:
						Window.displayText("Thats enough! Pay me at once or "\
										   "geddout.", 
										   Tavern.Bartender.name, 2)
						Window.displayText(self.name + " has no money, "\
											"and was thrown out.", "", 2)
						Tavern.branded.append(self.name)
				game_state.withLock(tab)
				return
		Window.displayText("Oie! Half-Orc! Betcha can't drink as much as I!",
						  self.name, 2)
		Window.displayText("Gahahaha! Mangy mortal, your puny stomach can't"\
						  " even contain one of my tankards.", "Imanorc", 2)
		Window.displayText("You're on! *glug* *glug* *chug* *glug* *glug*",
						   self.name, 2)
		Window.displayText("Issat all you got? *gloug* *gloug* *choug* "\
						   "*gloug* *gloug*", "Imanorc", 2)
		Window.displayText("After almost clearing "+Tavern.name+" out of ale,",
						   "", 2)
		Window.displayText("*Hic* Howwabout we armwrestle an whoever wins"\
						   " picksupthe tab?", self.name, 2)
		Window.displayText("Arright, pun-*hic*-y warrior.", "Imanorc", 2)
		Window.displayText(self.name + " wants to armwrestle Imanorc", "", 1)
		if self.Event.wait(SHORTWAIT) is False:
			self.Event.clear()
			Window.displayText("Grrrrghhh!!!! Why you so strronng???", 
						       self.name, 2)
			Window.displayText("Gahahaha! Weakling.", "Imanorc", 2)
			Window.displayText("Imanorc crushes "+self.name+"'s hand for fun.",
							   "", 2)
			def got_crushed():
				self.health -= 5
				self.health = max(0, self.health)
				health -= 5
				if self.money <= 0:
					Tavern.tab[self.name] = Tavern.tab.get(self.name, 0) + 5
				else:
					self.money -= 5
					self.money = max(0, self.money)
			game_state.withLock(got_crushed)
		else:
			self.Event.clear()
			roll = random.randint(0, 20) + self.anger # simple d20 - athletics
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				Window.displayText("*BANG* Ha! I Win!!", self.name, 2)
				Window.displayText("Nooo!! How could this be!", "Imanorc", 2)
				def win():
					self.money  += 5
					health += math.ceil((self.max_health - self.health) * 0.1)
					self.health += math.ceil((self.max_health - self.health) \
						           * 0.1)
					self.health = min(self.max_health, self.health)
					self.drunkeness += 5
				game_state.withLock(win)
			else:
				Window.displayText("Grrrrghhh!!!! Why you so strronng???", 
									self.name, 2)
				Window.displayText("Gahahaha! You're so weak.", "Imanorc", 2)
				Window.displayText(self.name+"'s arm is strained.", "", 2)
				def got_strained():
					self.health -= 3
					self.health = max(0, self.health)
					health -= 3
					if self.money <= 0:
						Tavern.tab[self.name] = Tavern.tab.get(self.name, 0) + 5
					else:
						self.money -= 5
						self.money = max(0, self.money)
				game_state.withLock(got_strained)
		self.Event.clear()
		return (health, game_state)

	# someone is flirting with me:
	def flirt_me(self, game_state, Flirtername):
		self.Event.clear()
		# If I know about the monster, share that information:
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Flirter = People[Flirtername]
		if self.ready2battle.is_set():
			Window.displayText("Yo, I heard there's a dragon."\
				               " Help me slay it!", self.name, 2)
			Window.displayText("Ok. But I also slayed an Ogre once.",
								 Flirtername, 2)
			Window.displayText("Man, I don't care, you doin' this or what?",
								self.name, 2)
			Window.displayText("Urgh, fine. I'll bombard you with my "\
							   "heroic feats later.", Flirtername, 2)
			game_state.withLock(lambda:Flirter.ready2battle.set())
		# otherwise, tell them to go away:
		else:
			Window.displayText("You know, I slayed an Ogre once.", 
								Flirtername, 2)
			Window.displayText("Man, don't disturb me.", self.name, 2)

		# message to send to Flirter:
		sending = self.msg_cmds["flirt"]
		msg = ExpiringMessage(self.name, (sending[1]), LONGWAIT)
		PostOffice.send_built_Message(self.name, Flirtername, msg)
		# set the Asker's internal event to signal we sent them a message:
		game_state.withLock(lambda:Flirter.InternalEvent.set())
		return

	# flirt with another fighter:
	def flirt_fighter(self, game_state, Flirter):
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		# message to send to Victim:
		sending = self.msg_cmds["flirt"]
		msg = ExpiringMessage(self.name, (sending[0], self.name), LONGWAIT)
		PostOffice.send_built_Message(self.name, Flirter, msg)
		msg.clear()
		self.Event.clear()
		if msg.read == True:
			self.InternalEvent.wait()
			#  get mail from victim
			mail_from = PostOffice.get_Mail_From(Flirter, self.name)
			received = sending[1]
			for msg in mail_from:
				if msg.content == (received):
					return (True, game_state)
			return (True, game_state) # just in case 

		return (False, None)


	def flirt(self, game_state, Person):
		self.Event.clear()
		People = game_state.Characters()
		Window = game_state.Window()
		Window.displayText("The "+ self.name +" saunters up to " + Person, 
						   "", 2)
		Window.displayText("The "+self.name+" wants to flirt with " + Person,
		                   "", 1)
		if self.Event.wait(SHORTWAIT) is False:
			Window.displayText(Person + " ignores the " + self.name, "", 2)
			return (0, game_state)
		self.Event.clear()
		Window.displayText("The "+self.name+" waits for "+Person+" to respond.",
		                   "", 2)
		
		# if the Victim is a fighter:
		if People[Person].fighter == True: 
			read = False
			(read, new_game_state) = self.flirt_fighter(game_state, Person)
			self.Event.clear()
			if read == True:
				return (0, new_game_state)
			else:
				return (0, game_state)

		# Ask the NPC:
		Flirter = self.name
		Window.displayText("The "+Person+" turns to the "+Flirter, "", 2)
		roll = random.randint(0, 20) + self.flirter # simple d20 - persuasion
		if People[Flirter].Alignment is "good":
			if roll >= 10:
				Window.displayText("I used to think love() was abstract, "\
								   "until you implemented it in MyHeart.",
								    Flirter, 2)
				dic_succ = "There's more of my functions in your class"
				ext_succ = [(Person, "Oh, that's not the only thing I've "\
							"put in your class"),
							(Person, "But if you want access to my private"\
							" functions, you need to do something for me."),
							(Flirter, "I'll do anything for love()"), 
							(Person, "Slay a terriplasty dragon in the "\
							"dungeon and give me its gold."),
							(Flirter, "and I will do that!")]
				dic_fail = "Uh, I'm an Erlang programmer."
				ext_fail = [(Person, "Uh, I'm an Erlang programmer. I don't "\
							"go anywhere near classes--especially abstract"\
							" ones."),
							(Flirter, "I can be functional! Give me another"\
							" chance!"), 
							(Person, "...fine.")]
			else:
				Window.displayText("Oh, "+Person+", if I had a star for every"\
								   " time you've brightened my day, I'd have"\
								   " a galaxy", Flirter, 2)
				dic_succ  = "Haha."
				ext_succ  = [(Person, "Your name must be Andromeda, cause"\
							 " we are destined to collide"),
							 (Flirter, "Oh that's a good one."), 
							 (Person, "If you wanna hear more, kill a dragon"\
							 " for me."),
							 (Flirter, "Done and done! I'll be back before "\
							 "you know it!")] 
				dic_fail  = "*Slap* Ew, don't come near me."
				ext_fail  = [(Person, "*Punch* Get away from me, loser."), 
							(Flirter, "Ow. I respect your decision, goodbye."),
							 (Person, "*sigh* I was a bit too harsh...you'll"\
							 " have a minute to convince me.")]
		else:
			if roll >= 10:
				Window.displayText("If I was an OS your process would have"\
								   " top priority", Flirter, 2)
				dic_succ = "You're right! I've never starved when I'm "\
						   "with you."
				ext_succ = [(Person, "So I'll never be starved waiting "\
							"for you?",),
							(Flirter, "I promise, you'll even be free of "\
							"deadlocks if you share a room with me."),
							(Person, "Ah, but I'm afraid I need to use your"\
							" CPU time for something else."),
							(Person, "There's a terriplasty dragon haunting "\
							"the streets. Go bring its corpse to me and I'll"\
							" release my lock in your empty room."),
							(Flirter, "Will do! That mcdragin dragon is dead!")]
				dic_fail = "Sorry, but I'm dead to your locks."
				ext_fail = [(Person, "Kill my thread now cause I'm dead to"\
							" your locks."), 
				            (Flirter, "Wait! Please give me another chance!"),
				            (Person, "...fine")]
			else:
				Window.displayText("Are you the square root of -1? Cause you"\
								   " can't be real", Flirter, 2)
				dic_succ = "I do need to integrate some curves."
				ext_succ = [(Person, "Are you proficient in integrating my"\
							" curves?"), 
							(Flirter, "I never learned calculus, but I bet "\
							"you could teach me."),
							(Person, "If you wanna be my ward, you must prove"\
							" yourself first."),
							(Person, "Wrestle with the mighty dragon that "\
							"lives in the dungeon and bring back an ear."),
							(Person, "Only then I will teach you how to take"\
							" tangents.")]
				dic_fail = "...How did you know?"
				ext_fail = [(Person, "How did you know I'm not real?"), 
							(Person, "I've been trying to get back to the "\
							"Polar Plane for years."),
							(Person, "Do you know the way?"), 
							(Flirter, "No, but I can brighten your day"\
							" instead!")]
			
		if People[Flirter].zombie:
			Window.displayText("I'm also a zombie. Can I eat you?", 
								Flirter, 2)
		
		prompt = Flirter + " rolled a "+ str(roll)+ ". How should " + \
				 Person + " respond to " + Flirter +"?"
		dic = {"0":dic_succ, "1":dic_fail}
		Window.print_options(dic, prompt)
		if Window.Event.wait(LONGWAIT) is True:
			Window.Event.clear()
			if Window.command == "0":
				for (speaker, dialogue) in ext_succ:
					Window.displayText(dialogue, speaker, 2)
				def flirt_succ():
					self.ready2battle.set()
					People[Flirter].flirted_with.append(Person)
				game_state.withLock(flirt_succ)
			elif Window.command == "1":
				for (speaker, dialogue) in ext_fail:
					Window.displayText(dialogue, speaker, 2)
				# simple d20 - persuasion
				roll = random.randint(0, 20) + self.flirter 
				if self.Alignment == "chaotic":
					if roll >= 10:
						Window.displayText("I give you epsilon, you give"\
										   " me delta. Together, we find "\
										   "limits!", Flirter, 2)
						dic_succ = "You're under my big O notation."
						ext_succ = [(Person, "I can surround you in my "\
									"big O, but you've gotta tighten your"\
									" lower bound."),
									(Person, "Killing a dragon can help. "\
									"There's one in the dungeons outside "\
									"town."),
									(Person, "Slay it, and we can talk "\
									"later.")]
						dic_fail = "Sorry but your asymptote diverges "\
								   "from mine."
						ext_fail = (Person, "I am limitless, so please "\
								   "diverge away from me.")
					else:
						Window.displayText("Did you cast singularity? Cause "\
										   "the closer I get to you, the "\
										   "faster time slips by.", FLirter, 2)
						dic_succ = "Only to pull you in closer."
						ext_succ = [(Person, "My sphere will slowly drain "\
								   "your energy if you don't kill a dragon."),
									(Flirter, "Uh..ok? I guess I can battle"\
									" one."), (Person, "It's in the dungeon. "\
									"Go get it.")]
						dic_fail = "The field's going to detonate in 3 "\
								   "seconds."
						ext_fail = [(Person, "My field is going to detonate "\
									"in 3 seconds, wiping away everything in"\
									" 5 meters."),
									(Person, "I suggest you leave.")]
				else:
					if roll >= 10:
						Window.displayText("Hey "+Person+", if you were a "\
										   "chicken, you'd be impeccable  "\
										   "( ͡° ͜ʖ ͡°)", Flirter, 2)
						dic_succ = "Yeah, I guess I can accept that."
						ext_succ = [(Person, "If you want to skin a chicken,"\
									" you first need to carve up a dragon."),
									(Person, "There's one in the dungeon."), 
									(Flirter, "Great! I'll cook one up for "\
									"you!")]
						dic_fail = "If you were an egg, you'd be smelly "\
								   "and rotten, like your pick-up lines."
						ext_fail = [(Person, "Go die.")]
					else:
						Window.displayText("Are you made of copper and "\
										   "tellurium? Because you're CuTe",
										   Flirter, 2)
						dic_succ = "Whatever, lets get this over with."
						ext_succ = [(Person, "I need some dragon parts, go to"\
									" the dungeon and get me some."),
									(Flirter, "ok.")]
						dic_fail = "How did you know I'm an android?"
						ext_fail = [(Person, "I thought no one could see "\
									"through my disguise as an organic. How "\
									"did you know?"),
									(Flirter, "Uh, cause you're CuTe?"), 
									(Person, "Ha..nice try, but no.")]
				prompt = "How should " + Person + " respond?"
				dic.clear()
				dic = {"0":dic_succ, "1":dic_fail}
				Window.print_options(dic, prompt)
				if Window.Event.wait(LONGWAIT) is True:
					Window.Event.clear()
					if Window.command == "0":
						for (speaker, dialogue) in ext_succ:
							Window.displayText(dialogue, speaker, 2)
						def flirt_succ():
							self.ready2battle.set()
							People[Flirter].flirted_with.append(Person)
						game_state.withLock(flirt_succ)
					else:
						for (speaker, dialogue) in ext_fail:
							Window.displayText(dialogue, speaker, 2)
						Window.displayText("That was terrible.", Person, 2)
						Window.displayText("Don't speak to me again.",
						Person, 2)
						
			else:
				Window.displayText("GAARGHH?!! Go away " + self.name + "!!",
								   Person, 2)
				Window.displayText("Or I'll make you.", Person, 2)
		else:
			Window.displayText(Person + " ignores the " + self.name, "", 2)
		Window.displayText("", "", 2)
		Window.displayText("", "", 2)
		return (0, game_state)

	# utility function for flirting:
	def flirt_utility(self, game_state):
		People = game_state.Characters()
		people_list = list(People)
		people_list.remove(self.name)
		victim = people_list[random.randint(0, len(people_list) - 1)]
		try:
   			if People[victim].barkeep:
   				return(1000, 1000, victim)
		except AttributeError:
			return (random.randint(0, 10), 10, victim)



	# attack the monster!
	def attack(self, finished, Monster, game_state):
		self.Event.clear()
		Window = game_state.Window()
		#turnstile for starting game:
		Window._DungeonMaster__Lock.acquire()
		Window._DungeonMaster__Lock.release()

		if self.health < 5:
			Window.displayText(self.name + " is breathing heavily; their face"\
						" is scrunched up, blood drenching their clothes.", 
						"", 2)
		# Shambles up to the Dragon -- skips first turn
		# Can grab the dragon - test -, making it vunerable to attacks
		# Dragon has a chance to break from grapple, sends the zombie 
		# flying, must then shamble back up again.
		if self.zombie:
			if self.shambles >= 1:
				Window.displayText("GhhrRrhhr...*wrap*", self.name, 2)
				Window.displayText(self.name + " wants to grab the " +
								   Monster.name, ">", 1)
				self.Event.clear()
				
				if self.Event.wait(LONGWAIT) is False:
					self.Event.clear()
					Window.displayText(self.name + " fails to grab " +\
									   Monster.name, "", 2)
					Window.displayText("Ha! Puny zombie! Face my Wings!"\
									   " *Whoosh*", Monster.name, 2)
					Window.displayText(self.name +" was pushed back!", "<", 2)
					Window.displayText(self.name +" must now shamble "\
									   "forward again.", "<", 2)
					Window.displayText("", "", 1)
					self.shambles = 0
					return
				else:
					self.Event.clear()
					roll = random.randint(1, 20)  # simple d20 - acrobatics
					prompt = self.name + " rolled a " + str(roll)+\
							", do they succeed?"
					dic = {"s":"success", "f":"failure"}
					Window.print_options(dic, prompt)
					if Window.Event.wait(LONGWAIT) is True: 
						Window.Event.clear()
						if Window.command is "s":
							Window.displayText(self.name+ " grabs the "+\
											   Monster.name+"! "+Monster.name+\
											   " is now vunerable to attacks!",
											   "<")
							with Monster.Lock():
								Monster.health -= 3
								if Monster.health <= 0:
									finished.set()
							return
					Window.displayText(self.name + " fails to grab " +\
									   Monster.name, "", 2)
					Window.displayText("Ha! Puny zombie! Face my Wings!"\
									   " *Whoosh*", Monster.name, 2)
					Window.displayText(self.name +" was pushed back!", "<", 2)
					Window.displayText(self.name +" must now shamble "\
									   "forward again.", "<", 2)
					Window.displayText("", "", 1)
					self.shambles = 0
					return
			else:
				Window.displayText(self.name+" shambles towards "+\
					 			   Monster.name, "", 2)
				Window.displayText("One day you'll face my wrath!", 
								   self.name, 2)
				return

		elif self.drunkeness >= 5:
			# do one powerful attack with advantage.
			Window.displayText(self.name+ " positions themselves to punch " +\
							   Monster.name, "", 2)
			Window.displayText(self.name+" wants to punch "+Monster.name, ">", 
								2)
			roll1 = random.randint(1, 20)
			roll2 = random.randint(1, 20)
			if roll1 >= roll2: roll = roll1
			else: roll = roll2
			if self.Event.wait(LONGWAIT) is False:
					self.Event.clear()
					Window.displayText(self.name+" punches through the air,"\
						               " trips on a rock, and hits themself "\
						               "insead.", "<", 2)
					self.health -= 3
					self.health = max(self.health, 0)
					self.drunkeness -= 1
					self.drunkeness = max(self.drunkeness, 0)
					# drunkeness decreases by one.
					return
			self.Event.clear()
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				damage = random.randint(1, 20) + (2 * self.anger)
				Window.displayText("Hiiiyyaa!", self.name, 2)
				Window.displayText(self.name+" flies through the air "\
					               "and punches "+Monster.name+" dealing "+\
					               str(damage)+" damage!", "<", 2)
				with Monster.Lock():
					Monster.health -= damage
					Monster.health = max(0, Monster.health)
					if Monster.health <= 0:
						finished.set()
				return
			else:
				Window.displayText(self.name+" punches through the air,"\
					               " trips on a rock, and hits themself "\
					               "insead.", "<", 2)
				self.health -= 3
				self.health = max(self.health, 0)
				self.drunkeness -= 1
				self.drunkeness = max(self.drunkeness, 0)
				return
		else:
			if "The Old Man" in self.flirted_with:
				Window.displayText(self.name + " saunters up to the "+\
								   Monster.name, "<", 2)
				Window.displayText(self.name + " wants to flirt with "+\
								   Monster.name, "<", 1)

				if self.Event.wait(LONGWAIT) is False:
					self.Event.clear()
					Window.displayText(Monster.name +" ignores "+self.name,
									   "", 2)
					Window.displayText("", "", 1)
					return
				self.Event.clear()
				
				Window.displayText("Oh, what large teeth you have!",
								   self.name, 2)
				Window.displayText("ARRGGOOOARHH", Monster.name, 2)
				Window.displayText("I mean, white sparkly teeth! I know "\
								   "you probably hear this all the time "\
								   "from your food, but you must use "\
								   "bleach or something cause that's "\
								   "one dazzling smile you got there!",
								   self.name, 2)
				Window.displayText("*purrrrrrs*", Monster.name, 2)
				with Monster.Lock():
					Monster.flirted = self.name
				finished.set()
				return
			Window.displayText(self.name+ " is channelling their inner rage!", "", 1)
			Window.displayText("I've come here to fight things and chew gum.",
							    self.name, 2)
			Window.displayText("And I'm all out of gum.", self.name, 2)
			if self.Event.wait(LONGWAIT) is False:
				self.Event.clear()
				Window.displayText(Monster.name +" ignores "+self.name+\
								  "'s taunts","", 2)
				Window.displayText("Argh! I need you to respond so I can "\
								   "fight you!", self.name, 2)
				Window.displayText("", "", 1)
				return
			roll = random.randint(1, 20)
			self.Event.clear()
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				damage = random.randint(1, 12) + self.anger + \
				         random.randint(1, 12)
				Window.displayText("Raaarrwwrrr!", self.name, 2)
				Window.displayText(self.name+" sprints towards "+Monster.name+\
					               "and cleaves their axe through their face,"\
					               " dealing "+str(damage)+" damage!", "<", 2)
				with Monster.Lock():
					Monster.health -= damage
					Monster.health = max(0, Monster.health)
					if Monster.health <= 0:
						finished.set()
				return
			else:
				Window.displayText(self.name+" runs towards "+Monster.name+\
					               ", but trips on a rock, and hits themself "\
					               "insead.", "<", 2)
				self.health -= 4
				self.health = max(self.health, 0)
				self.drunkeness -= 1
				self.drunkeness = max(self.drunkeness, 0)
				return	
		return 