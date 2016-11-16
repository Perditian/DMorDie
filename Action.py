"""
 Avita Sharma
 Action Class
 Creates, evaluates, and performs an action
 Note: Need a better reward/penalty system for updating probability of
 action success

 TODO: MAKE UTILITY FUNCTION ~NEGATIVE SIGMOID
""" 

class Action:

	# Actions are a collection of two functions and an initial probability
	# of success. There is the action function and the expected action function
	# the action function does the action, and the action utility function 
	# returns the utility if the action was performed
	def __init__(self, fun_action = None, expected = None, success = 0.5):
		self.success = success
		self.action = fun_action
		self.action_utility = expected
		self.expected_utility = 0
		self.total_utility = 0
		self.action_args = None

	# performs and evaluates action, updates probability of success
	# accordingly
	def perform(self, game_state):
		(actual_utility, game_state) = self.action(game_state, self.action_args)
		print("My success: " + str(self.success))
		amount = 0
		if self.total_utility != 0:
			amount = actual_utility / self.total_utility

		if actual_utility is None:
			# we reached a contradiction; do nothing:
			print("OBJECTION! *FINGER POINT* THERE'S A CONTRADICTION!\n")
			return game_state
		elif actual_utility >= self.expected_utility:
			# increase success by amount of success:
			print("I succeeded by: " + str(amount) + "\n")
			self.success = min(1.0, self.success * (1 + amount))
		else:
			# decrease success by amount of failure:
			# Note: there is always a miniscule chance of success!
			print("I failed by: " + str(amount) + "\n")
			self.success = max(0.001, self.success *  amount)
		print("My new success: " + str(self.success))
		return game_state

	# save the expected utility calculation and returns it.
	# action_utility returns the maximum utility gained if the action was done,
	# and the corresponding arguments to trigger the maximum utility outcome.
	# it also returns the total utility available for this action 
	def expected(self, game_state):
		(self.expected_utility, self.total_utility, self.action_args) = \
		                        self.action_utility(game_state) 
		self.expected_utility *= self.success
		print ("This action has expected utility: " + str(self.expected_utility))
		print ("This action has total utility: " + str(self.total_utility))
		return self.expected_utility
