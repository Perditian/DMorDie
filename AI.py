"""
 Avita Sharma
 Artificial Intelligence Class
 Provides a template for the AIs

 AIs have a dictionary of Goals, where the keys are the Goals and the values
 are a tuple of the Goal Weight and a dictionary of Actions.
 The Goal Weights are initialized once and never changed.
 Actions have the function name of the action as keys, and a probability of
 success as values.

 AIs also have an overall level of trust in the DM.
 This influences their choice of actions involving the DM. (I.E. whether to
 	follow the DM's advice, or not.)

TODO: add concurrency, DM's interrupt feature, etc.
""" 

import random
import Action
import threading
import time

class AI:

	# initialize with a list of Goals, Weights, and Actions.
	# |Goals| == |Weights| == |Actions|
	# Goals is a list of strings, weights is a list of doubles,
	# and Actions is a dictionary of Actions (class), indexed by 0...n
	def __init__(self, Goals = {}, Weights = [], Actions = {}, Trust = 1, 
		         Name = "This is my unique Identifier/Name", health = 15,
		         fighter = False, Location = None):
		goals = {}
		i = 0
		for g in Goals:
			goals[g] = (Weights[i], Actions[str(i)])
			i += 1
		self.Goals = goals
		self.DMtrust = Trust
		self.name = Name
		self.Lock = threading.Lock()
		self.Event = threading.Event()
		self.InternalEvent = threading.Event()
		self.ready2battle = threading.Event()
		self.kill = threading.Event()
		self.health = health
		self.dead = False
		self.fighter = fighter
		self.Location = Location
		self.zombie = False

		self.msg_cmds = {"pickpocket":["pickpocket you", "been pickpocket"],
		                 "ask":["ask you", "been ask"], 
		                 "kill":["kill you", "been kill"],
		                 "flirt":["flirt you", "been flirt"]}

	# right now: determined completely randomly
	# returns the set of actions for the decided goal
	def decide_goal(self, exclude = []):
		goal  = self.Goals.keys()
		goals = [self.Goals[x] for x in goal if x not in exclude]
		names = [x for x in goal if x not in exclude]
		rand  = random.randint(0, len(goals) - 1)
		print("I decided to " + names[rand])
		(w, goal_actions) = goals[rand]
		return (goal_actions, names[rand])

	# decide actions based on the expected utility of the action, and the
	# level of trust in the DM
	# TODO: invoke randomness/do stupid decisions
	# NOTE: for testing, once a goal has no more profitable actions, I kill
	# myself.
	def decide_actions(self, actions, game_state):
		max_utility = 0
		Window = game_state.Window()
		best_action = None
		for action in actions:
			utility = action.expected(game_state) * self.DMtrust
			if utility > max_utility:
				max_utility = utility
				best_action = action
		return best_action
	
	# used by other characters to lock this thread:
	def lock_me(self):
		self.Lock.acquire()
		
	# used by other characters to unlock this thread:
	def unlock_me(self):
		self.Lock.release()
	
	# NOTE: this assumes a message-handling class that is passed with the game_state
	# For now, messages are functions which take in the AI and Game State as parameters
	# Good reason for polymorphic functions --> pass in NPCs or DM instead of AI
	def handle_messages(self, game_state):
		MailBox = game_state.Messages()
		Mail = [msg for msg in MailBox.get_Mail(self.name) if msg.valid == True]
		for msg in Mail:
			if msg.valid:
				msg.readme()
				(text, args) = msg.content
				if text is (self.msg_cmds["pickpocket"])[0]:
					self.pickpocket_me(game_state, args)
				elif text is (self.msg_cmds["ask"])[0]:
					self.ask_me(game_state, args)
		#		elif text is (self.msg_cmds["kill"])[0]:
		#			self.kill_me(game_state, args)
		#		elif text is (self.msg_cmds["flirt"])[0]:
		#			self.flirt_me(game_state, args)
			return
		
	# basic loop for the AI to follow, runs forever.
	def life(self, game_state):
		Life = True
		while Life:
			# I am in battle, stop doing actions: (kill thread)
			if self.kill.is_set():
				Window = game_state.Window()
				Window.displayText(self.name + " goes to the Dungeon.", "", 2)
				return
			# First Handle Messages, Resolve messages before proceeding
			self.handle_messages(game_state)
			goalist = []
			action = None
			# if there are no profitable actions to do, I prepare for battle:
			while action is None:
				if len(goalist) == len(self.Goals.keys()):
					Window = game_state.Window()
					Window.displayText(self.name+" is ready to do battle!!", "", 2)
					self.ready2battle.set()
					# reset the goalist, so I continue to do actions
					# until the party is all ready to battle:
					goalist = [] 
					with self.Lock:
						continue

				# decide the goal, then the action:
				(goal, index) = self.decide_goal(goalist)
				action = self.decide_actions(goal, game_state)
				goalist.append(index)

			# used to lock myself, perform an action:
			with self.Lock:
				game_state = action.perform(game_state)