"""
 Avita Sharma
 Battle and Monster class

 Basic Idea: create a thread which checks the GameState if all 
 Playable Characters are ready for battle. If they are, it waits for their 
 current actions to complete, then sends everyone to battle!
""" 

import threading
import random
from GameState import *

LONGWAIT = 20
SHORTWAIT = 15
REALLYSHORTWAIT = 5


# The Monster Class, only dragons are implemented currently:
class Dragon:

	def __init__(self, name, health = 30):
		self.name = name
		self.health = health
		self.fly_away = 0
		self.__lock = threading.Lock()
		self.flirted = False


	def Lock(self):
		return self.__lock

	# attack the characters, if I kill them all or 
	# fly away, set finished to true:
	def attack(self, finished, GameState):
		Window = GameState.Window()
		#turnstile for starting game:
		Window._DungeonMaster__Lock.acquire()
		Window._DungeonMaster__Lock.release()

		prompt = "What should the dragon do?"
		dic = {"0":"attack!", "1":"Fly away"}
		Window.print_options(dic, prompt)
		# wait for DM to choose an option:
		if Window.Event.wait(LONGWAIT) is True:
			Window.Event.clear()
			# Dragon decides to attack
			#### NOTE: should include a test to see if their attack hits. ####
			if Window.command == "0":
				self.fly_away = 0
				People = GameState.Characters()
				prompt = "Who should the dragon attack?"
				dic.clear()
				i = 0
				for (name, person) in People.items():
					if person.fighter:
						dic[str(i)] = name
						i += 1
				dic[str(i)] = "themself"
				Window.print_options(dic, prompt)
				# wait for DM to choose a person to attack:

				#turnstile for pausing game:
				Window._DungeonMaster__Lock.acquire()
				Window._DungeonMaster__Lock.release()
				if Window.Event.wait(LONGWAIT) is True:
					Window.Event.clear()
					Player = dic[Window.command]
					dam = random.randint(0, 20) #normal d20
					Window.displayText("The Dragon attacks "+Player+" and deals "+str(dam)+" damage", "", 1)
					if Player == "themself":
						self.health -= dam
						if self.health <= 0:
							finished.set()
					else:
						# attack the player
						People[Player].health -=dam
						try:
							People[Player].lounge = False
						except AttributeError:
							pass
						if not People[Player].zombie:
							People[Player].health = max(0, People[Player].health)
							if People[Player].health <= 0:
								Window.displayText("Oh no! "+Player+" is in critical condition!!", "", 2)
								People[Player].dead = True
			# Dragon decides to fly away, takes 2 consecutive actions:
			elif Window.command == "1":
				if self.fly_away == 0:
					Window.displayText("The Dragon is preparing to fly away!", "", 2)
					Window.displayText("The Dragon can flee next turn.", "", 1)
				else:
					Window.displayText("The Dragon bursts into the sky", "", 2)
					Window.displayText("It flees to another village, out of your reach.", "", 2)
					finished.set()
				self.fly_away += 1
			return
		# DM did not interact on time, do something horrible:
		dam = random.randint(0, 20) + 10 #normal d20
		self.health -= dam
		Window.displayText("The dragon attacked itself!", "", 2) 
		Window.displayText(self.name +" has "+str(self.health)+" health left.", "", 1)
		if self.health <= 0:
			finished.set()
		return

	# The battle is finished, decide outcome:
	def finishedBattle(self,GameState):
		Window = GameState.Window()
		if self.health <= 0:
			Window.displayText("The dragon is dead. You loot its corpse.", "", 2)
			Window.displayText("You find 100 gold for everyone!!", "", 2)
			Window.displayText("There's a note in the dragon's pocket.", "", 2)
			Window.displayText("It reads: 'The Princess is in another castle.'", "", 2)
			Window.displayText("          'Ha! Suckers. ~ Old Man'", "", 2)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			
			People = GameState.Characters()
			with GameState.Lock():
				for (n, person) in People.items():
					if person.fighter:
						person.Money += 100
						Window.displayText(n + " leaves with "+str(person.Money) + " gold!", "", 2)
		elif self.fly_away > 1:
			Window.displayText("You see the dragon soaring away.", "", 2)
			Window.displayText("Your weapons don't reach and your taunts", "", 2)
			Window.displayText("do no damage. FLuttering down is a note.", "", 2)
			Window.displayText("It reads: 'The Dragon is now in another castle.'","", 2)
			Window.displayText("          'Ha! Losers. ~ Old Man'", "", 2)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			
		else:
			Window.displayText("The Dragon looks at your corpses disappointingly.", "", 2)
			Window.displayText("How vexing. I thought they were better...", "Dragon", 2)
			Window.displayText("The Dragon shapes back into the Old Man.", "", 2)
			Window.displayText("Well, time to find a stronger group! Hehehehe...", "Old Man", 2)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
			Window.displayText("", "", 1)
		Window.displayText("", "", 2)
		Window.displayText("", "", 2)
		Window.displayText("", "", 1)
		Window.displayText("", "", 1)
		Window.displayText("SEE YOU NEXT CAMPAIGN!", "", 2)
		Window.displayText("SEE YOU NEXT CAMPAIGN!", "", 1)
		return


# Battle class!
class Battle(object):

	def __init__(self):
		self.finished = threading.Event()	

	# check if all fighters are ready to battle, if they are, send them
	# to battle:
	def life(self, Monster, threads, GameState):
		People = GameState.Characters()
		all_ready = False
		Fighters = []
		for person in People.values():
				if person.fighter:
					Fighters.append(person)

		while all_ready is False:
			all_ready = True
			for fighter in Fighters:
					all_ready = all_ready and fighter.ready2battle.is_set()
			if all_ready:
				print("we are all ready!!")
				# kill all fighter threads:
				for fighter in Fighters:
					fighter.kill.set()
				for thread in threads:
					thread.join()
				# do battle!:
				order = self.prepare4battle(Monster, GameState)
				self.doBattle(order, Monster, GameState)
				Monster.finishedBattle(GameState)
				# # restart threads:
				#for person in People.values():
				#	thread = person.life(...)
				# 	thread.start()
		return

	# prepare for the battle:
	def prepare4battle(self, Monster, GameState):
		Window = GameState.Window()
		Window.displayText("", "", 2)
		Window.displayText("", "", 2)
		Window.displayText("", "", 2)
		Window.displayText("", "", 1)
		Window.displayText("", "", 1)
		Window.displayText("", "", 1)
		Window.displayText("IT'S BATTLE TIME!", "", 1)
		Window.displayText("IT'S BATTLE TIME!", "", 2)
		Window.displayText("", "", 2)
		Window.displayText("", "", 1)

		Window.displayText("The party enters the dungeon; they smell something dank and rotting.", "", 2)
		Window.displayText("They see a cracked path in the wall, and decide to investigate", "", 2)
		Window.displayText("Entering the small cavern, the sound of wings beat upwards.", "", 2)
		Window.displayText("ROAAAAAARRGH!!", Monster.name, 2)
		Window.displayText("Who dares disturb me peace!", Monster.name, 2)
		Window.displayText("The party quivers in fright!", "", 2)
		Window.displayText("But they muster up their courage, and begin to fight!", "", 2)
		"""
		what should happen:
		Turn based: Playable Characters, then DM
		-> First Roll initiative to see the turn order
		Then:
			PC turn: they all go in initiative order or at the same time?,
			do their attacks -> need DM to see if they succeed?

			DM turn: is the monster. Can do multiple attacks.

		Battle ends:
			When the Monster's health is 0
			When all characters are dead
			Or something else...?

		"""
		# if order > 0.5 -> DM goes first
		order = random.random()
		return order

	# let all the characters attack concurrently:
	def Characters_attack(self, Monster, GameState):
		Window = GameState.Window()
		People = GameState.Characters()
		threads = []
		# make a thread for each fighter attack function:
		for (n, p) in People.items():
			if p.fighter:
				if not p.zombie and p.health <= 0:
					Window.displayText(n+" is dead...", "", 2)
				else:
					threads.append(threading.Thread(target=p.attack, args=(self.finished, Monster, GameState,)))
		for t in threads:
			t.start()
		for t in threads:
			t.join()
		return

	# check if we meet a win condition:
	# (all living fighters are dead, or the monster is dead):
	def win_yet(self, Monster, GameState):
		People = GameState.Characters()
		healthsum = 0
		for person in People.values():
			if person.fighter:
				health = person.health
				if health > 0:
					healthsum += health
		if healthsum <= 0:
			self.finished.set()
		if Monster.health <= 0:
			self.finished.set()
		return

	# fight! If order > 0.5, Monster goes first:
	def doBattle(self,order, Monster, GameState):
		while self.finished.is_set() is False:
			if order > 0.5:
				Monster.attack(self.finished, GameState)
				self.win_yet(Monster, GameState)
				if self.finished.is_set() is False:
					self.Characters_attack(Monster, GameState)
			else:
				self.Characters_attack(Monster, GameState)
				self.win_yet(Monster, GameState)
				if self.finished.is_set() is False:
					Monster.attack(self.finished, GameState)
		return
