# UltimateTicTacToe
MCTS powered ultimate tic tac toe
Project Name: Ultimate Tic Tac Toe

Project theme: Artificial intelligence and machine learning project in Python.

System Expertise: The system expertise is flexible and allows for a change in the difficulty level resulting in a change in the standby time for the computer queue. The longer the computer's turn, the higher the difficulty level. It is difficult to estimate the winning percentages of the computer, since each game depends on the human player playing and other factors. Therefore the percentage of victory depends on the level of difficulty chosen by the user. The longer the queue of the computer, the greater the chance of winning.

Background: Deep Blue is a computer developed by IBM for the game of chess. In 1997 there was a battle between world champion Gary Kasparov and the computer and this was the first time that a computer won a world chess champion. Deep Blue practiced aglorametics that determined how good the board condition was for him and with its help he decided what the next step would be. The problem is that this type of algorithm did not apply to all games, for example for the body game. In these cases another type of algorithm is suitable such as the Monte Carlo Tree Search - MCTS.
In 2017 AlphaGo Zero was introduced, which used the MCTS algorithm in such a way that it was not necessary to analyze data from games played by people, but rather that the algorithm played against itself and in this way it learned the best moves to reach victory.

Algorithmics (machine learning, artificial intelligence):
The Monte Carlo method is a method of solving computational problems using random numbers.
Monte Carlo algorithms are computational algorithms that plot random numbers a large number of times and perform calculations on the numbers drawn.
The main use of the algorithm is to solve problems that cannot be solved accurately mathematically, or to save computing power.
The structure of the algorithm is as follows:
Step One: Defines a space of possible inputs to the algorithm.
Step Two: The inputs are selected by a computer from the possible input space by using a certain probability function activated on that space.
Third stage: A certain deterministic calculation is calculated on these inputs.
Step Four: The statistics of all results are collected and displayed.

How does this algorithm work in the game?
Suppose I am currently in a specific board mode. Instead of looking at all the possible moves I can play from the current situation, I choose a few possible moves according to their 'strength'. Strength is the value of a node given to them in the simulation phase as a default value, the strength is also determined by the number of "visits" to that node, as the node is sampled more times its strength increases.
For each leaf in an extended tree, I play the game randomly until a decision is made, until I win or lose.
 The win or loss is rolled back and used to correct the strength assessment of the situations I encountered along the way.
This process of expansion and simulations runs until the end of the time set for the computer.

Implementation: The project is implemented in the Python language and consists of several engines:
Artificial Intelligence Engine: The realization of MCTS algorithms and its adaptation to the Ultimate Tic Tac Toe game. Realization of a number of game modes such as player vs. computer and player vs. player vs. computer at different difficulty levels that are defined by running algorithms run times.
Graphic engine: Using the Tkinter library to create a board on which there is a two-dimensional matrix of 3x3 subboards. The graphical engine serves as a proxy between the intelligence engine and the game model that is responsible for all calculations and input tests in the system.
Model Engine: The model engine is responsible for running the game properly and continuously, with no bugs and no exceptions during the run. The motor is responsible for the output and input in the system, for checking their integrity. Through this engine the game settings are selected and displayed graphically on the game. The model engine is responsible for transmitting the appropriate and correct data between the various departments in the code:
