"""
Avita Sharma, Eric Wyss, Davis Taus
Rogue Class, extends AI

Rogues can:
	(*) Pickpocket other characters
	(*) Steal from buildings
	(*) Ask characters for money
	(*) Attack monsters in battle
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

class Rogue(AI):

	def __init__(self, Alignment = 0, name = "Rogue", Home = None):
		if Alignment is 0:
			self.Alignment = 'chaotic'
			self.sleight = 5
			self.persuasion = 3
			pickpocket_success = 0.6
			stealing_success = 0.4
		else:
			self.Alignment = 'good'
			self.sleight = 3
			self.persuasion = 5
			pickpocket_success = 0.4
			stealing_success = 0.6

		Pickpocketing = Action(self.pickpocket, self.pickpocket_utility, 
			                   pickpocket_success)
		Stealing = Action(self.steal, self.stealing_utility, stealing_success)
		Asking = Action(self.ask, self.ask_utility, 1)
		
		Goals = ['Make Money', 'Ask']
		Weights = [0.5, 0.5]
		Actions = {str(0):[Pickpocketing, Stealing], str(1):[Asking]}

		# make an AI with 0.5 trust in the DM, 10 health, a fighter, and
		# home
		AI.__init__(self, Goals, Weights, Actions, 0.5, name, 10, True, Home)
		self.Money = 0
		self.counter = 0
		self.lounge = False

	# asks the DM if an event succeeds or fails:
	def success_or_fail(self, Window, prompt = None):
		Window.print_options({'s':'success', 'f':'failure'}, prompt)
		if Window.Event.wait(LONGWAIT) is True:
			Window.Event.clear()
			if Window.command == 's':
				return True
		return False

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

	# someone is killing me!
	def kill_me(self, game_state, Perpname):
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Perpetrator = People[Perpname]
		health_taken = 0
		Attacker = Perpname
		Victim = self.name
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
			# simple d20 - hit roll, penalized since I noticed:
			roll = random.randint(0, 20) - Perpetrator.anger
			roll = max(1, roll)
			prompt = Perpname + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				# simple d12 - hit roll
				roll = random.randint(0, 12) + Perpetrator.anger 
				def hit():
					self.health -= roll
					self.health = max(1, People[Victim].health)
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
				Window.displayText("The " + Attacker + " swings their "\
					               "axe and misses!!", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		def end_fight():
			Perpetrator.Event.clear()
			Perpetrator.drunkeness -= 1
			Perpetrator.drunkeness = max(0, Perpetrator.drunkeness)
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


	# determines the maximum utility gained from pickpocketing one person,
	# returns the max utility, the total utility, and the best victim
	# for pickpocketing:
	def pickpocket_utility(self, game_state):
		People = game_state.Characters()
		Window = game_state.Window()
		max_money = 0
		total_money = 0
		victim = None
		for (name, person) in People.items():
			if name != self.name:
				total_money += person.Money
				if person.Money >= max_money:
					max_money = person.Money
					victim = name
		return (max_money, total_money, victim)


	# this Rogue pickpockets the Victim:
	def pickpocket(self, game_state, Victim):
		self.Event.clear()
		People = game_state.Characters()
		Window = game_state.Window()
		Money_Earned = People[Victim].Money
		Window.displayText("The " + self.name + " creeps up to " + \
		                   Victim, self.name, 2)
		Window.displayText("The " + self.name + " wants to pickpocket " +\
		                   Victim, "", 1)
        
		# if the Victim is a fighter, they can fight back:
		if People[Victim].fighter == True:  #FIX ME
			read = False
			(read, rate, new_game_state) = \
			                       self.pickpocket_fighter(game_state, Victim)
			self.Event.clear()
			if read == True:
				return (rate, new_game_state)
			else:
				return (None, game_state)

    	# wait for the DM to interact with this event:
		if self.Event.wait(SHORTWAIT) is False:
			# the DM did not interact, do something horrible:
			Window.displayText("The " + self.name + \
				               " attempted to pickpocket " + Victim, "<", 2)
			Window.displayText("And failed miserably. They lost 10gp.", 
				               "<", 2)
			def pickfail():
				People[self.name].Money -= 10
				People[self.name].Money = max(0, People[self.name].Money)
			game_state.withLock(pickfail)
			Window.displayText("The " + self.name + " now has " +\
			                   str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			# the DM interacted, now see if I succeed:
			roll = random.randint(0, 20) + self.sleight # simple d20 - sleight of hand
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				# I succeeded, now I pickpocket the Victim for all their money:
				def picksucc():
					Money_Earned = People[Victim].Money
					People[self.name].Money += Money_Earned
					People[Victim].Money = 0
				game_state.withLock(picksucc)
				Window.displayText("The " + self.name + \
					               " pickpocketed " + Victim + " for " +\
					               str(Money_Earned) + " zenny!!", "<", 2)
			else:
				# I failed:
				Window.displayText("The " + self.name + " failed!!", "<", 2)
			Window.displayText("The " + self.name + " now has " + \
				               str(People[self.name].Money) + " zenny", "<", 1)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		self.Event.clear()
		return (Money_Earned, game_state)

	# I pickpocket another fighter:
	def pickpocket_fighter(self, game_state, Victim):
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Money_Earned = People[Victim].Money
		# message to send to Victim:
		sending = self.msg_cmds["pickpocket"]
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

	# I am being pickpocketed!
	def pickpocket_me(self, game_state, Perpetrator):
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Money_Lost = self.Money 
		self.Event.clear()
		People[Perpetrator].Event.clear()
		# wait for the DM to interact with this event
		if People[Perpetrator].Event.wait(SHORTWAIT) is False:
			# DM did not interact, do something horrible:
			Window.displayText("The " + Perpetrator + \
				               " attempted to pickpocket " + self.name, "<", 2)
			Window.displayText("Ha! You lousy " + \
				               Perpetrator+".", self.name, 2)
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
			roll = random.randint(1, 20) - self.sleight # simple d20 
			roll = max(1, roll)
			myroll = random.randint(1, 20) 
			prompt = Perpetrator + " rolled a " + str(roll)+", and "+\
			         self.name+ " rolled a "+ str(myroll)+", does "+\
			         Perpetrator+" succeed?"
			cmd = self.success_or_fail(Window, prompt)
			# DM decided that the Perpetrator succeeded:
			if cmd:
				def picksucc():
					People[Perpetrator].Money += Money_Lost
					self.Money = 0
				game_state.withLock(picksucc)
				Window.displayText("The " + Perpetrator +\
				                   " pickpocketed " + self.name + \
				                   " for " + str(Money_Lost) + \
				                   " zenny!!", "<", 2)
			# DM decided that the Perpetrator fails:
			else:
				Window.displayText("The " + Perpetrator + " failed!!", "<", 2)
				Money_Lost = 0
				Window.displayText("The " + self.name + " now has " +\
				                    str(People[self.name].Money) + \
				                    " zenny", "<", 1)
				Window.displayText("", "", 2)
				Window.displayText("", "", 2)
				Window.displayText("", "", 1)
		# clear Perpetrator's event, so the DM can interact with them again:
		game_state.withLock(lambda:People[Perpetrator].Event.clear())

		"""
		WE NEED 2 SEND THE VICTIM A MESSAGE: 
		("You tried to pickpocket me", MONEY_LOST)
		"""
		# message to send to Victim:
		sending = self.msg_cmds["pickpocket"]
		msg = ExpiringMessage(self.name, (sending[1], Money_Lost), LONGWAIT)
		PostOffice.send_built_Message(self.name, Perpetrator, msg)
		# set the Perpetrator's internal event to 
		# signal we sent them a message:
		game_state.withLock(lambda:People[Perpetrator].InternalEvent.set())
		return


	# steal from buildings (i.e. the Village or Tavern)
	def steal(self, game_state, Victim):
		self.Event.clear()
		Places = game_state.Locations()
		People = game_state.Characters()
		Window = game_state.Window()
		Window.displayText("The " + self.name +\
			               " sneaks up to " + Victim, "", 2)
		Window.displayText("The "+self.name +\
			               " wants to steal from " + Victim, "", 1)
		Money_Earned = 0
		# wait for the DM to interact with this event:
		if self.Event.wait(SHORTWAIT) is False:
			# DM did not interact, do something horrible:
			Window.displayText("Oh no! The " + self.name + \
				               " got caught stealing :(", "<", 2)
			Window.displayText(self.name + " had to pay " +\
			                   str(self.Money) + " in fines.", "<", 2)
			self.Money = 0
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		else:
			# DM is interacting, do I succeed at stealing?
			roll = random.randint(0, 20) + self.sleight # simple d20 
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			cmd = self.success_or_fail(Window, prompt)
			if cmd:
				# I succeeded! Steal all their gold
				Money_Earned = Places[Victim].Money
				def steal_succ():
					People[self.name].Money += Money_Earned
					Places[Victim].Money = 0
				game_state.withLock(steal_succ)
				Window.displayText("The "+self.name+" stole from " +\
				                   Victim + " for " + str(Money_Earned) +\
				                   " zenny!!", "<", 2)
			else:
				# I failed...
				Money_Earned = 0
				Window.displayText("The "+self.name+" failed!!", "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
		# clear my event so that the DM can interact with me again
		self.Event.clear()
		return (Money_Earned, game_state)

	# get my maximum utility, total utility, and best victim for stealing:
	def stealing_utility(self, game_state):
		Places = game_state.Locations()
		Window = game_state.Window()
		max_money = 0
		total_money = 0
		victim = None
		for (name, place) in Places.items():
			total_money += place.Money
			if place.Money >= max_money:
				max_money = place.Money
				victim = name
		return (max_money, total_money, victim)

	# plead for money from Person:
	# If I'm chaotic, I don't learn about the monster
	# If I'm good, I learn about the monster and am now ready for battle!
	def plead(self, Window, Person):
		if self.Alignment == "chaotic":
			Window.displayText("Fine, didn't like you much anyway.", 
				               self.name, 2)
		else:
			Window.displayText("No! Please! I'm desperate for cash!", 
				               self.name, 2)
			Window.displayText("I'll do anything! ANYTHING.", self.name, 2)
			Window.displayText("Urgh, fine. There's a dragon.", Person, 2)
			Window.displayText("Go slay it, and I MIGHT give "\
				               "ye a coin or two.", Person, 2)
			Window.displayText("The " +self.name+" considers the offer...", 
				               "", 2)
			Window.displayText("", "", 2)
			Window.displayText("", "", 2)
			self.ready2battle.set()
		return


	# someone is asking me:
	def ask_me(self, game_state, Askername):
		self.Event.clear()
		# If I know about the monster, share that information:
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		Asker = People[Askername]
		if self.ready2battle.is_set():
			Window.displayText("Yo, I heard there's a dragon."\
				               " Help me slay it!", self.name, 2)
			Window.displayText("Ok.", Asker.name, 2)
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

	# I ask another fighter:
	def ask_fighter(self, game_state, Victim):
		People = game_state.Characters()
		Window = game_state.Window()
		PostOffice = game_state.Messages()
		# message to send to Victim:
		sending = self.msg_cmds["ask"]
		msg = ExpiringMessage(self.name, (sending[0], self.name), LONGWAIT)
		PostOffice.send_built_Message(self.name, Victim, msg)
		msg.clear()
		self.Event.clear()
		if msg.read == True:
			self.InternalEvent.wait()
			#  get mail from victim
			mail_from = PostOffice.get_Mail_From(Victim, self.name)
			received = sending[1]
			for msg in mail_from:
				if msg.content == (received):
					return (True, game_state)
			return (True, game_state) # just in case 

		return (False, None)

	# ask a person for money, depending on dialogue options, I can learn
	# information about a monster, and get ready to battle.
	def ask(self, game_state, Person):
		self.Event.clear()
		People = game_state.Characters()
		Window = game_state.Window()
		Window.displayText("The "+ self.name +" walks up to " +\
		                   Person, "", 2)
		Window.displayText("The "+self.name+" wants to talk to " +\
		                   Person, "", 1)

		# wait for the DM to interact with me:
		if self.Event.wait(SHORTWAIT) is False:
			# DM did not interact, nothing happens:
			Window.displayText(Person + " ignores the " + self.name, "", 2)
			return (0, game_state)
		
		Window.displayText("The "+self.name+" waits for "+\
			               Person+" to respond.", "", 2)

		# if the Victim is a fighter, they can fight back:
		if People[Person].fighter == True: 
			read = False
			(read, new_game_state) = self.ask_fighter(game_state, Person)
			if read == True:
				return (0, new_game_state)
			else:
				return (0, game_state)

		# Ask the NPC:
		People[Person].ask_me(game_state, self.name)

		self.Event.clear()
		Window.displayText("", "", 2)
		Window.displayText("", "", 2)
		return (0, game_state)


	# ask utility is random, person is random:
	def ask_utility(self, game_state):
		People = game_state.Characters()
#		people_list = People.keys()
		people_list = list(People)
		people_list.remove(self.name)
		victim = people_list[random.randint(0, len(people_list) - 1)]
		return (random.random() * 100, random.random() * 100, victim)
		#return (random.randint(0, 1), 1, victim)

	# attack the monster!
	def attack(self, finished, Monster, game_state):
		self.Event.clear()
		Window = game_state.Window()
		#turnstile for starting game:
		Window._DungeonMaster__Lock.acquire()
		Window._DungeonMaster__Lock.release()

		# I decided to lounge in the back, doing nothing:
		if self.lounge is True:
			Window.displayText(self.name +\
				               " lounges in the back, doing nothing.", "", 2)
			return
		# I'm in critical condition!
		if self.health < 5:
			Window.displayText(self.name + " is breathing heavily; "\
				              "their face is scrunched up, blood drenching "\
				              "their clothes.", "", 2)

		# I decide to steal from the Monster:
		if random.random() < 0.5:
			Window.displayText(self.name + " becomes invisible, "\
				               "inching towards the " + Monster.name +\
				               "'s pile of gold.", "", 2)
			Window.displayText(self.name + " wants to steal from the " +\
			                   Monster.name, "<", 1)
			# wait for the DM to interact with me:
			if self.Event.wait(LONGWAIT) is False:
				# The DM does not interact, something horrible happens:
				self.Event.clear()
				Window.displayText(self.name + " tries to do something, "\
					               "fails, and hurts themself.", "<", 2)
				self.health -= 2
				return
			# DM is interacting with me, do I succeed?
			roll = random.randint(1, 20) + self.sleight # simple d20 - sleight of hand
			prompt = self.name + " rolled a " + str(roll)+", do they succeed?"
			dic = {"s":"success", "f":"failure"}
			Window.print_options(dic, prompt)
			# wait for DM to choose an option:
			if Window.Event.wait(LONGWAIT) is True:
				Window.Event.clear()
				if Window.command is "s":
					# I succeeded!
					Window.displayText(self.name+ " steals 10gp from "+ \
						               Monster.name, "", 2)
					Window.displayText("ROAAARRRWR!! Me Gold!! Not me Gold!!",
					                   Monster.name, 2)
					Window.displayText(Monster.name+" bites their lip in "\
						               "disgust; their teeth pierce their "\
						               "skin and draw blood.", "", 2)
					with game_state.Lock():
						self.Money += 10
					with Monster.Lock():
						Monster.health -= 10
						if Monster.health <= 0:
							finished.set()
				else:
					# I failed...
					if roll > 15:
						Window.displayText(self.name + \
							      " glares at the Dungeon Master |:<", "", 1)
					Window.displayText("Swiper no swiping!", Monster.name, 2)
					Window.displayText("Swiper no swiping!", Monster.name, 2)
					Window.displayText("Swiper no swiping!", Monster.name, 2)
					Window.displayText("Oh, man!", self.name, 2)
					Window.displayText(self.name + \
						              " failed to steal any gold.", "<", 1)
				self.Event.clear()
				return
		else:
			# I decide to talk to the Monster:
			Window.displayText(self.name + " wants to talk to the "+ \
				                Monster.name, ">", 1)
			Window.displayText(self.name + " waltzs up to the " + \
				               Monster.name, "", 2)
			# Wait for DM to interact with me:
			if self.Event.wait(LONGWAIT) is False:
				# DM did not interact, do something horrible:
				Window.displayText(self.name + " tries to do something, "\
					               "fails, and hurts themself.", "<", 2)
				self.health -= 2
				return
			# DM is interacting with me, do I succeed?
			roll = random.randint(1, 20) + self.persuasion  # simple d20 - persuasion check
			Window.displayText(self.name + " rolled a " + str(roll) +\
			                   " on their persuasion check.", "", 1)
			prompt = "How does " + Monster.name+ " respond?"
			dic = {"0":"How dare ye! Face my flames instead!", 
			       "1":"Hm...I'll listen to what ye have to say."}
			Window.print_options(dic, prompt)
			# wait for DM to choose an option:
			if Window.Event.wait(LONGWAIT) is True: 
				Window.Event.clear()
				if Window.command is "0":
					Window.displayText("How dare ye think ye can "\
						               "speak with me!", Monster.name, 2)
					Window.displayText("Face my spit instead, cretein!", 
						               Monster.name, 2)
					Window.displayText(Monster.name+" spits fire all "\
						               "over the "+self.name +"!", "", 2)
					self.health -= 3
					return
				elif Window.command is "1":
					Window.displayText("...Ye has 3 mins to say what "\
						               "ye needs to say.", Monster.name, 2)
					if self.Alignment is "chaotic":
						Window.displayText("I'm just here for the money.", 
							               self.name, 2)
						Window.displayText("Pay me, and I'll leave you alone.", 
							               self.name, 2)
						dic0 = "Here's 100gp to attack the guy next to you."
						# find another fighter to hurt:
						victim = None
						People = game_state.Characters()
						for (name, person) in People.items():
							if person.fighter:
								if name != self.name:
									if person.dead is False:
										victim = name
										break
						if victim is not None:
							extended0 = [(Monster.name, "Here's 100 gold "\
								          "to attack " + victim),
							             (self.name, "Ok."), 
							             ("", self.name +" throws a knife "\
							              "into " + victim),
							             (victim, "WTH?!?! OW! Curse your "\
							              "sudden but inevitable betrayal!")]
						else: # I'm the only fighter:
							extended0 = [(self.name, "...I'm the only one "\
								         "here...right?"), 
							             (Monster.name, "Hehehehe...")]
					else: # I'm good:
						Window.displayText("Why, good sir, are you "\
							               "attacking villagers?", 
							               self.name, 2)
						dic0 = "None of ye beezwax, busta"
						Who = Monster.name
						extended0 = [(self.name, "But sir! I'm sure we can "\
							          "reach an agreement."), 
						             (Who, "*Sigh*, If ye must know, it's "\
						             	   "cause I hate'm."),
						             (self.name, "...Why?"), (Who, "They "\
						             "called me names. Foul names. "\
						             "Unspeakable names."),
						             (self.name, "Like 'terriplasty "\
						             "mcdragin on'?"), (Who, "Worse! Like "\
						             "'Whydoesthisdragonspeak' and "\
						             "'I'mnotanoldmangoshdarnit'"),
						             (self.name, "Hm, those are some pretty "\
						             "terrible names."), 
						             (self.name, "I guess you are justified "\
						             "in your murderous rampage."),
						             (self.name, "Well, then, carry on fine "+\
						             Who), 
						             (self.name, "I'll just be lounging back "\
						             "there.")]
					prompt = "How does the "+Monster.name+" respond?"
					dic.clear()
					dic = {"0":dic0, "1":"ALL THE FLAMES!!"}
					Window.print_options(dic, prompt)
					# wait for DM to choose:
					if Window.Event.wait(LONGWAIT) is True: 
						Window.Event.clear()
						if Window.command is "0":
							for (name, dia) in extended0:
								Window.displayText(dia, name, 2)
							if self.Alignment is "chaotic":
								# I got paid to hurt someone else:
								if victim is not None:
									People = game_state.Characters()
									with game_state._GameState__Lock:
										People[victim].health -= 5
										self.Money += 100
							else:
									# I'm good and decided to lounge around.
									self.lounge = True
						else:
							Window.displayText("How dare ye think ye can "\
								               "speak with me!", "Dragon", 2)
							Window.displayText("Face my spit instead, "\
								               "cretein!", "Dragon", 2)
							Window.displayText(Monster.name+" spits fire all "\
											"over the "+self.name+"!", "", 2)
							self.health -= 3
						self.Event.clear()
						return
		# this happens when the DM decided not to choose an option:
		self.Event.clear()
		Window.displayText(self.name + " tries to do something, fails, and "\
			               "hurts themself.", "", 2)
		self.health -= 2
		return

