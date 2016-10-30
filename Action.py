"""
 Avita Sharma
 Action Class
 Creates, evaluates, and performs an action
""" 

class Action:

	# default success, no action function.
	def __init__(self):
		self.success = 0.5
		self.action = None
		self.expected = None
		self.expected_utility = 0

	# Actions are a collection of two functions and an initial probability
	# of success. There is the perform function and the expected function
	def __init__(self, fun_action, expected, success):
		self.success = success
		self.action = fun_action
		self.expected = expected

	# performs and evaluates action, updates probability of success
	# accordingly
	def perform(self, game_state):
		(actual_utility, game_state) = self.action(game_state)
		if actual_utility is None:
			# we reached a contradiction; do nothing:
			return game_state
		else if actual_utility > self.expected_utility:
			# increase success by amount of success:
			amount = (actual_utility - self.expected_utility) / actual_utility
			self.success = min(1.0, self.success * (1 + amount))
		else
			# decrease success by amount of failure:
			# Note: there is always a miniscule chance of success!
			amount = (self.expected_utility - actual_utility) / self.expected_utility
			self.success = max(0.001, self.success *  (1 - amount))
		return game_state

	# save the expected utility calculation and returns it.
	def expected(self, game_state):
		self.expected_utility = self.expected(game_state) * self.success
		return self.expected_utility