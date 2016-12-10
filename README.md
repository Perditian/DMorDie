# DMorDie
Concurrent DMing Game

To Install:
	clone /DMorDie/ from github

To Run:
Linux: ./DMorDie


Windows: python3 DMorDie.py


How To Play:
type i Name to interrupt a Character when they try to do something.


Github address:
https://github.com/Perditian/DMorDie

# Code Overview:
|File Name		|Description									 |
|-----------------------|:------------------------------------------------------------------------------:|
|AI.py			|Generalizes how each Playable Character functions.				 | 
|			|Includes common fields for all characters. (AI class)				 |
|Action.py	        |Maps the action to its utility, updates the action based on performance.	 |
|Battle.py		|Includes the Monster and Battle Class.  					 |
|DMorDie.py		|Main Program, run to play game. Initializes and runs the game. 		 |
|DungeonMaster.py	|The GUI class. Creates and updates the GUI.					 |
|GameState.py		|The Game State class. A collection of shared memory under a monitor. 		 |
|NPC_and_Location.py	|The NPC and Location classes. NPC extends AI. 					 |
|Rogue.py		|The Rogue Class. A Playable Character, includes the actions to send 		 |
|			|to the AI class, and an Attack function for the Battle. 			 |
|Warrior.py		|The Warrior Class. A Playable Character, includes the actions to send 		 |
|            		|to the AI class, and an Attack function for the Battle. 			 |
|expiringObject.py	|Includes the expring messages to send with the Post Office. 			 |
|postOffice.py		|Handles messaging between Playable Characters. Messages are expiring messages.
