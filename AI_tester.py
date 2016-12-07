"""
 Avita Sharma, Eric Wyss, David Taus
 DM or DIE!!
 Main game loop
"""

from AI import AI 
from Action import Action
from Rogue import Rogue
# from Warrior import Warrior
import threading
import random
from DungeonMaster import DungeonMaster
from GameState import GameState
from postOffice import PostOffice
from Battle import *
import sys

try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *

from math import ceil

class NPC (AI):
	
	def __init__(self, name = 'The Old Man', money = 100, Home = None):
		AI.__init__(self, Location = Home)
		self.name = name
		self.Money = money
		self.flirted = []

	# for Rogues who ask the NPCs:
	# in future, when we expand the NPC classes, we can vary the dialogue:
	def ask_me(self, game_state, Askername):
			Window = game_state.Window()
			People = game_state.Characters()
			Asker = People[Askername]
			Window.displayText("The "+self.name+" turns to the "+Asker.name, "", 2)
			prompt = "How should " + self.name + " greet the " + Asker.name +"?"
			dic = {"0":"Well Hello there, weary Traveler...", "1":"GAH! A " + Asker.name + "! Get away from me!!"}
			Window.print_options(dic, prompt)
			# wait for DM to choose a dialogue option:
			if Window.Event.wait(LONGWAIT) is True:
				Window.Event.clear()
				if Window.command == "0":
					Window.displayText("Well Hello there, weary Traveler.", self.name, 2)
					Window.displayText("What brings you to this flashy " + self.name +"?", self.name, 2)

					if Asker.Alignment == "chaotic":
						Window.displayText("Need some money, bro.", Asker.name, 2)
						dic0 = "Got gold for ye, but there's a price..."
						extended0 = [(self.name, "I got some gold for ye, but"), (self.name, "it comes with a price."), \
									(Asker.name, "...I need to pay for free money?"), (self.name, "Aie, not with ye gold, but with ye body."), \
									(Asker.name, "WHAT?!"), (self.name, "There's a dragon need'n some slay'n."),(self.name," You do that, you get me gold."), \
									(Asker.name, "Oh, that's what you meant..."),(Asker.name, "I'll consider it.")]
					else:
						Window.displayText("Yo, you got any quests with rewards?", Asker.name, 2)
						dic0 = "There's a dragon need'n some slay'n"
						extended0 = [(self.name, "You in need of quest? Har Har Har!"),(self.name," A quest I got for ye."), \
						             (self.name, "I heard there's a violent,"),(self.name,"vicious dragon haunting the land"), \
						             (self.name, "Slay that beast, and I'll give ye my thanks."), \
						             (self.name, "..also some gold, I guess."), (Asker.name, "Many thanks, my good " + self.name +", I'll kill it immediately!")]
					prompt = "How should " + self.name + " respond?"
					dic.clear()
					dic = {"0":dic0, "1":"You know what? I don't like your attitude."}
					Window.print_options(dic, prompt)
					if Window.Event.wait(LONGWAIT) is True:
						Window.Event.clear()
						if Window.command == "0":
							for (speaker, dialogue) in extended0:
								Window.displayText(dialogue, speaker, 2)
							# Asker is ready for battle!
							with game_state.Lock():
								Asker.ready2battle.set()
						else:
							Window.displayText("You know what? You're too shady.", self.name, 2)
							Window.displayText("I don't deal with sketchy characters.", self.name, 2)
							Asker.plead(Window, self.name)
				else:
					# DM chose choice 1: GAH! Get away from me!
					Window.displayText("GAARGHH?!! You foul " + Asker.name + ".", self.name, 2)
					Window.displayText("I have no business with you.", self.name, 2)
					Asker.plead(Window, self.name)
			else:
				# DM timed out on choosing an option, nothing happens
				Window.displayText(self.name + " ignores the " + Asker.name, "", 2)
			return

class Location():

	def __init__(self, name = "the Don't Go Inn", money = 150, health = 10):
		self.name = name
		self.Money = money
		self.health = health
		self.max_health = health
		self.branded = [] # list of people ostracized from the location


def main():    
	Tavern = Location('The Don\'t go Inn', health = 30)
	barkeep = NPC("Anita Colbier", 0)
	barkeep.barkeep = True
	Tavern.Bartender = barkeep
	barkeep.Location = Tavern
	Tavern.Tavern = True

	Village = Location("Rock Bottom Village", 0)
	Village.Village = True

	rogue = Rogue(0, Home = Village)
	rogue1 = Rogue(1, 'Assasin', Village)
	#warrior = Warrior(1, Location = Village)
	#warrior1 = Warrior(1, Location = Village, Name = "Paladin")

	OldMan = NPC(Home = Village)

	# create the main window:
	window = Tk()
	window.geometry("1328x755")
	window.config(bg = "#99ff99")
	DM = DungeonMaster(window)

	# opening prompt:
#	prompt  = "Hi Dungeon Master, welcome to your new campaign!"
#	prompt0 = "There are characters for you to interrupt (i). You can"
#	prompt1 = "also print (p) a list of characters and actions "
#	prompt2 = "if you forget. Spelling counts!"
#	prompt3 = "Press any button to start the game."

#	DM.displayText(prompt, "", 1)
#	DM.displayText(prompt0, "", 1)
#	DM.displayText(prompt1, "", 1)
#	DM.displayText(prompt2, "", 1)

	boxes = PostOffice()
	for name in [rogue.name, rogue1.name]:
		boxes.add_Name(name)


	game_state = GameState(boxes, {rogue.name:rogue, rogue1.name:rogue1, OldMan.name:OldMan,
					barkeep.name:barkeep},
		         {Tavern.name:Tavern, Village.name:Village}, DM)

	DM.set_GameState(game_state)

	dagon = Dragon("Menacing Dragon")


	# create the Dungeon Master thread:
	#DM_thread = threading.Thread(target=DM.life, args=(game_state,))
	#DM_thread.start()

	# this "ensures" that the window will be open before the threads start
	# writing to it.
	def start_with_delay(thread):
			thread.start()
			return

	# create an AI thread:
	Rogue_thread = threading.Thread(target=rogue.life, args=(game_state,))
	Rouge_delay = threading.Timer(1.0, start_with_delay, [Rogue_thread])
	Rouge_delay.start()
	

	Rogue_thread1 = threading.Thread(target=rogue1.life, args=(game_state,))
	Rouge_delay1 = threading.Timer(1.0, start_with_delay, [Rogue_thread1])
	Rouge_delay1.start()


	battle = Battle()
	Battle_thread = threading.Thread(target=battle.life, args=(dagon,
		            [Rogue_thread, Rogue_thread1], game_state))
	Battle_thread.start()

	Window_thread = threading.Thread(target=window.mainloop())
	Window_thread.start()

	Battle_thread.join()
	Window_thread.join()
	#Rogue_thread.join()
	#Rogue_thread1.join()

	
	#DM_thread.join()


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

