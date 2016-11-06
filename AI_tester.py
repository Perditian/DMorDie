"""
 Avita Sharma
 
 TESTS FOR AI AND ACTIONS

 In Future: game_state should have the state, messaging, and lock
"""

from AI import AI 
from Action import Action
import threading
import random

def pickpocket_utility(game_state):
	(People, _, _) = game_state
	max_money = 0
	total_money = 0
	victim = None
	for (name, person) in People.items():
		print(name + " has " + str(person.Money) + " zenny\n")
		if name != 'Rogue':
			total_money += person.Money
			if person.Money >= max_money:
				max_money = person.Money
				victim = name
	return (max_money, total_money, victim)

def pickpocket(game_state, Victim):
	(People, Mess, Lock) = game_state
	Money_Earned = People[Victim].Money
	People['Rogue'].Money += Money_Earned
	People[Victim].Money = 0
	print("The Rogue pickpocketed " + Victim + " for " + str(Money_Earned) + " zenny!!\n")
	return (Money_Earned, (People, Mess, Lock))

# ideally this is for buildings/places, not people:
def steal(game_state, Victim):
	(People, Mess, Lock) = game_state
	if People['Rogue'].counter <= 0:
		Money_Earned = 0
		People['Rogue'].counter += 1
		print("Oh no! The Rogue got caught stealing :(\n")
	else:
		Money_Earned = People[Victim].Hidden_Money
		People['Rogue'].Money += Money_Earned
		People[Victim].Hidden_Money = 0
		print("The Rogue stole from " + Victim + " for " + str(Money_Earned) + " zenny!!\n")
	return (Money_Earned, (People, Mess, Lock))

def stealing_utility(game_state):
	(People, _, _) = game_state
	max_money = 0
	total_money = 0
	victim = None
	for (name, person) in People.items():
		print(name + " has " + str(person.Hidden_Money) + " hidden zenny\n")
		if name != 'Rogue':
			total_money += person.Hidden_Money
			if person.Hidden_Money >= max_money:
				max_money = person.Hidden_Money
				victim = name
	return (max_money, total_money, victim)


def default_action(game_state, N=None):
	MAX_UTILITY = 10000000
	(People, Mess, Lock) = game_state
	People['Rogue'].counter += 1
	if People['Rogue'].counter >= 2:
		print("I went to the dungeon and got eaten by a Troll.\n")
		exit(0)
	print("Waiting to go to dungeon...\n")
	return (MAX_UTILITY, game_state)

def default_utility(game_state):
	MAX_UTILITY = 10000000
	return (MAX_UTILITY, MAX_UTILITY)


def ask(game_state, Person):
	(People, Mess, Lock) = game_state
	print("The Rogue asks " + Person + " for money.")
	if random.random() > 0.5:
		print(Person + " replies, sure here you go!")
		People['Rogue'].Money += 100
		return (100, (People, Mess, Lock))
	print(Person + " replies, GET AWAY YOU MONSTER.")
	return (0, (People, Mess, Lock))


def ask_utility(game_state):
	(People, Mess, Lock) = game_state
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

	game_state = ({Rogue.name:Rogue, OldMan.name:OldMan, Tavern.name:Tavern}, None, None)

	# create an AI thread:
	Rogue_thread = threading.Thread(target=Rogue.life, args=(game_state,))
	Rogue_thread.start()
	Rogue_thread.join()
	return 






if __name__ == '__main__':
	main()

