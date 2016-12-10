
"""
 Avita Sharma, Eric Wyss, David Taus
 DM or DIE!!
 NPC and Location classes
"""

from AI import AI 
from GameState import *

class NPC (AI):
	
	def __init__(self, name = 'The Old Man', money = 100, Home = None):
		AI.__init__(self, Location = Home)
		self.name = name
		self.Money = money

	# for Rogues who ask the NPCs:
	# in future, when we expand the NPC classes, we can vary the dialogue:
	def ask_me(self, game_state, Askername):
			Window = game_state.Window()
			People = game_state.Characters()
			Asker = People[Askername]
			Window.displayText("The "+self.name+" turns to the "+\
				               Asker.name, "<", 2)
			prompt = "How should " + self.name + " greet the " + \
			          Asker.name +"?"
			dic = {"0":"Well Hello there, weary Traveler...", 
			       "1":"GAH! A " + Asker.name + "! Get away from me!!"}
			Window.print_options(dic, prompt)
			# wait for DM to choose a dialogue option:
			if Window.Event.wait(LONGWAIT) is True:
				Window.Event.clear()
				if Window.command == "0":
					Window.displayText("Well Hello there, "\
						               "weary Traveler.", self.name, 2)
					Window.displayText("What brings you to this flashy " + \
						               self.name +"?", self.name, 2)

					if Asker.Alignment == "chaotic":
						Window.displayText("Need some money, bro.", Asker.name, 2)
						dic0 = "Got gold for ye, but there's a price..."
						extended0 = [(self.name, "I got some gold for ye, but"), 
									(self.name, "it comes with a price."),
									(Asker.name, "...I need to pay "\
										         "for free money?"), 
									(self.name, "Aie, not with ye gold, "\
										        "but with ye body."),
									(Asker.name, "WHAT?!"), 
									(self.name, "There's a dragon "\
										        "need'n some slay'n."),
									(self.name,"You do that, you "\
										       "get me gold."), \
									(Asker.name, "Oh, that's "\
										         "what you meant..."),
									(Asker.name, "I'll consider it.")]
					else:
						Window.displayText("Yo, you got any quests "\
							               "with rewards?", Asker.name, 2)
						dic0 = "There's a dragon need'n some slay'n"
						extended0 = [(self.name, "You in need of quest? "\
							                     "Har Har Har!"),
									 (self.name," A quest I got for ye."),
						             (self.name, "I heard there's a violent,"),
						             (self.name,"vicious dragon haunting "\
						                        "the land Slay that beast, "\
						                        "and I'll give ye my thanks."),
						             (self.name, "..also some gold, I guess."),
						             (Asker.name, "Many thanks, my good " +\
						             self.name +", I'll kill it immediately!")]
					prompt = "How should " + self.name + " respond?"
					dic.clear()
					dic = {"0":dic0, 
					       "1":"You know what? I don't like your attitude."}
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
							Window.displayText("You know what? You're too "\
								               "shady. I don't deal with "\
								               "sketchy characters.", 
								               self.name, 2)
							Asker.plead(Window, self.name)
				else:
					# DM chose choice 1: GAH! Get away from me!
					Window.displayText("GAARGHH?!! You foul " + \
						               Asker.name + ".", self.name, 2)
					Window.displayText("I have no business with you.", 
						               self.name, 2)
					Asker.plead(Window, self.name)
			else:
				# DM timed out on choosing an option, nothing happens
				Window.displayText(self.name + " ignores the " +\
				                   Asker.name, ">>", 2)
			return



class Location():

	def __init__(self, name = "the Don't Go Inn", money = 150, health = 10):
		self.name = name
		self.Money = money
		self.health = health
		self.max_health = health
		self.branded = [] # list of people ostracized from the location

