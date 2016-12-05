"""
 Avita Sharma
 Action Class
 Creates, evaluates, and performs an action
 Note: Need a better reward/penalty system for updating probability of
 action success

 TODO: MAKE UTILITY FUNCTION ~NEGATIVE SIGMOID
""" 
import math

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

	# sigmoid function, used to evaluate performances
	def sigmoid(amount):
		return  -0.002 + (0.3 / (1 + math.exp(-10 * (x - 0.5)))))


	# performs and evaluates action, updates probability of success
	# accordingly
	def perform(self, game_state):
		Window = game_state.Window()
		(actual_utility, game_state) = self.action(game_state, self.action_args)
		#Window.displayText("My success: " + str(self.success), ">", 2)
		if actual_utility is None:
			# we reached a contradiction; do nothing:
			Window.displayText("OBJECTION! *FINGER POINT* THERE'S A CONTRADICTION!", ">", 2)
			return game_state

		# prevent division by zero:
		if self.expected_utility == 0:
				self.expected_utility = 0.0001

		actual_utility *= self.success
		if actual_utility >= self.expected_utility:
			# increase success by amount of success:
			amount = (actual_utility - self.expected_utility) / self.expected_utility
			self.success = min(1.0, self.success + success_sigmoid(amount))
		else:
			# decrease success by amount of failure:
			# Note: there is always a miniscule chance of success!
		#	Window.displayText("I failed by: " + str(amount), ">", 2)
			amount = (self.expected_utility - actual_utility) / self.expected_utility
			self.success = max(0.001, self.success -  failure_sigmoid(amount))
		#Window.displayText("My new success: " + str(self.success), ">", 2)
		return game_state

	# save the expected utility calculation and returns it.
	# action_utility returns the maximum utility gained if the action was done,
	# and the corresponding arguments to trigger the maximum utility outcome.
	# it also returns the total utility available for this action 
	def expected(self, game_state):
		Window = game_state.Window()
		(self.expected_utility, self.total_utility, self.action_args) = \
		                        self.action_utility(game_state) 
		self.expected_utility *= self.success
	#	Window.displayText("This action has expected utility: " + str(self.expected_utility),
	#		               ">", 1)
	#	Window.displayText("This action has total utility: " + str(self.total_utility),
	#						">", 1)
		return self.expected_utility
