from tkinter import *
from tkinter import ttk
import copy

import time
import random
from math import *
from copy import *


class Node():

   def __init__(self, parent, state, reachMove): #creates an empty node

       self.totalSimulations = 0
       self.score = 0
       self.children = []
       self.parent = parent
       self.state = state
       self.reachMove = reachMove

   def expand(self): #expands the current node, adds new node that contains the new move

       nextMoves, nextSymbol = self.state.getValidMoves(self.reachMove)
       for move in nextMoves:
           newBoard = deepcopy(self.state)
           newBoard.playMove(move, nextSymbol)
           newNode = Node(self, newBoard, move)
           self.children.append(newNode) #adds the new node to array of children of current node

   def backPropogate(self, result): #updates all parents of the current node according to the node's score and number of simulations
       self.totalSimulations += 1
       self.score += result

       if self.parent != None:  # Non-Root node
           self.parent.backPropogate(result)

   def getExplorationTerm(self): #a mathematic function that returns the exploration term of the current node

       return sqrt(log(self.parent.totalSimulations) / (self.totalSimulations or 1))#ratio between num of simulations from the parent compared to the simulations from the node

   def getExploitationTerm(self): #a mathematic function that returns the exploitation term of the current node

       return self.score / (self.totalSimulations or 1)#when average wins is high


class MCTS():

   def __init__(self, symbol, C=sqrt(2), compTime=2): #creates a new mcts object

       self.symbol = symbol
       self.C = C
       self.compTime = compTime  # In seconds
       self.opponentMap = {
           'X': 'O',
           'O': 'X'
       }

   def simulate(self, board, prevMove): #simulates random moves (and gameplay) until the time is up

       currState = board.getState()

       if currState[0] == 'N':
           nextMoves, nextSymbol = board.getValidMoves(prevMove)
           # Randmoly choose the next move
           randomMove = random.choice(nextMoves)

           board.playMove(randomMove, nextSymbol)

           return self.simulate(board, randomMove) #recursively simulating gameplay
       else:

           if currState[0] == 'W':
               if currState[1] == self.symbol:
                   return 1  # Win
               else:
                   return -1  # Loss
           else:
               return 0  # Draw

   def selection(self, currNode, symbol): #func that is in charge of the selection step, selecting the next node to expand and simulate on

       curState = currNode.state.getState()
       if curState[0] != 'N':  # Terminal node
           return currNode

       if len(currNode.children) == 0:  # Not expanded
           return currNode
       # Selecting best child based on exploration Term and exploitation term
       # Sort by exploration - exploitation tradeoff: child.getExploitationTerm() + self.C * child.getExplorationTerm()
       # The first component of the formula above corresponds to exploitation; it is high for moves with high average win ratio.
       # The second component corresponds to exploration; it is high for moves with few simulations.
       # The algorithm prefers moves with high average win ratios with low number of simulations.
       if symbol == self.symbol:
           sortedChildren = sorted(currNode.children,
                                   key=lambda child: child.getExploitationTerm() + self.C * child.getExplorationTerm(),
                                   reverse=True)
       else:
           sortedChildren = sorted(currNode.children, key=lambda
               child: -child.getExploitationTerm() + self.C * child.getExplorationTerm(), reverse=True)

       return self.selection(sortedChildren[0], self.opponentMap[symbol])

   def getMove(self, board, prevMove):

       # Creating a root node
       rootNode = Node(None, deepcopy(board), prevMove)
       # Monte Carlo Iterations
       startTime = time.time()
       while time.time() - startTime < self.compTime:
           selectedNode = self.selection(rootNode, self.symbol)  # Selection step

           if selectedNode.totalSimulations == 0:  # First simulation
               result = self.simulate(deepcopy(selectedNode.state), selectedNode.reachMove) #result of simulation
               selectedNode.backPropogate(result) #update the tree according to result
           else:  # Expansion
               selectedNode.expand()

       # Final move selection
       sortedChildren = sorted(rootNode.children, key=lambda child: child.getExploitationTerm(), reverse=True) #sorts nodes from highest to lowest exploit term
       return sortedChildren[0].reachMove #returns the move of the most exploited node


class Local:
   def __init__(self,idx):
       self.local=[0, 0, 0], [0, 0, 0], [0, 0, 0]
       self.idx=idx #each local board has a matching index

   def get_local(self):#func that returns the local board
       return self.local

   def getAllEmptySlots(self): #func that returns all empty slots in a local board
       slots = []
       if self.getState()[0] == 'N':
           for i in range(3):
               for j in range(3):
                   if self.local[i][j] == 0:
                       slots.append([i, j])
       return slots

   def playMove(self, move, symbol):#func that makes a move, places the selected sign in the required slot on the local board

       self.local[move[0]][move[1]] = symbol

   def getState(self):#func that checks if a win/tie ocurred in a local board

       # Horizontal check
       for i in range(3):
           if self.local[i][0] == self.local[i][1] and self.local[i][1] == self.local[i][2] and self.local[i][0] != 0:
               return 'W', self.local[i][0]

       # Vertical check
       for i in range(3):
           if self.local[0][i] == self.local[1][i] and self.local[1][i] == self.local[2][i] and self.local[0][i] != 0:
               return 'W', self.local[0][i]

       # Diagonal check
       if self.local[0][0] == self.local[1][1] and self.local[1][1] == self.local[2][2] and self.local[0][0] != 0:
           return 'W', self.local[0][0]
       if self.local[0][2] == self.local[1][1] and self.local[1][1] == self.local[2][0] and self.local[0][2] != 0:
           return 'W', self.local[0][2]

       # Draw Check
       for i in range(3):
           for j in range(3):
               if self.local[i][j] == 0:
                   return 'N', 0
       return 'D', 0

class Global:
   def __init__(self,graphics,gamemode):
       self.opponentMap = {
           'X': 'O',
           'O': 'X'
       }
       if gamemode=="Computer":
           self.local_list=[[Local(0),Local(1),Local(2)],
                            [Local(3),Local(4),Local(5)],
                            [Local(6),Local(7),Local(8)]]
       if gamemode=="Friend":
           self.local_list=[Local(0).local,Local(1).local,Local(2).local,Local(3).local,Local(4).local,Local(5).local,Local(6).local,Local(7).local,Local(8).local] #creates global board which consists of 9 local boards

   def playMove(self,move, symbol): #func that updates a local win on the global board
       self.local_list[move[0]//3][move[1]//3].playMove([move[0]%3, move[1]%3], symbol)

   def getState(self): #func that turns the global board into a local board and checks if a global win/tie ocurred

       # Creating a small Board version for easier computation
       smallVer = Local(0)
       for i in range(3):
           for j in range(3):
               curState = self.local_list[i][j].getState()

               if curState[0] == 'W':
                   smallVer.local[i][j] = curState[1]
       curState = smallVer.getState()
       if curState[0] == 'W':
           return 'W', curState[1]

       if len(self.getAllEmptySlots()) == 0:
           return 'D', '0'

       return 'N', '0'



   def convertIndToBig(self, empty, smallBoardInd):#converts board to 9x9 and returns all the empty spaces ( as 9x9 coordinates)
       for i in range(len(empty)):
           empty[i] = [3 * smallBoardInd[0] + empty[i][0], 3 * smallBoardInd[1] + empty[i][1]]#adds the coordinates of the empty places to empty array (in empty[0] we have the first empty 9x9 coordinate)
       return empty

   def getAllEmptySlots(self): #returns all empty spaces in the global board (as 9x9 coordinates)
       empty=[]
       for i in range(3):
           for j in range(3):
               empty+=self.convertIndToBig(self.local_list[i][j].getAllEmptySlots(), [i, j])
       return empty

   def getValidMoves(self,prevMove): #returns all  possible moves that can be played according to the current state of the game board
       if prevMove==None:
           return (self.getAllEmptySlots(),'X')

       smallBoardInd = [prevMove[0] % 3, prevMove[1] % 3]
       if self.local_list[smallBoardInd[0]][smallBoardInd[1]].getState()[0]!='N':
           return self.getAllEmptySlots(),self.opponentMap[self.local_list[prevMove[0]//3][prevMove[1]//3].local[prevMove[0]%3][prevMove[1]%3]]
       else:
           return (
           self.convertIndToBig(self.local_list[smallBoardInd[0]][smallBoardInd[1]].getAllEmptySlots(), smallBoardInd),
           self.opponentMap[self.local_list[prevMove[0]//3][prevMove[1]//3].local[prevMove[0]%3][prevMove[1]%3]])

   def get_local_list(self):
       return self.local_list

   def is_win(self,game_board, type): #func that checks if a local win occurred
       for i in range(3):
           if game_board[i][0] == type and game_board[i][1] == type and game_board[i][2] == type:
               return True
           if game_board[0][i] == type and game_board[1][i] == type and game_board[2][i] == type:
               return True
       if game_board[0][0] == type and game_board[1][1] == type and game_board[2][2] == type:
           return True
       if game_board[2][0] == type and game_board[1][1] == type and game_board[0][2] == type:
           return True
       return False

   def is_full(self,game_board): #func that checks if the global board is full
       count = 0
       for i in range(3):
           for j in range(3):
               if game_board[i][j] != 0:
                   count += 1
       return count == 9

class Module:
   def __init__(self,graphics):
       self.graphics=graphics
       self.global_state=[0,0,0],[0,0,0],[0,0,0]

   def init_golbal(self,gamemode):
       self.global1=Global(self.graphics,gamemode)



   def legal_click(self,num,idx): #func that makes sure that a move is legal
       if self.graphics.game_mode=="Friend":
           if self.get_global_board().get_local_list()[num[4]][num[2]-idx[1]][num[3]-idx[2]]!=0:
               return False
       if self.graphics.game_mode=="Computer":
           if self.get_global_board().local_list[int(num[2] / 3)][int(num[3] / 3)].get_local()[num[2] - idx[1]][num[3] - idx[2]]!=0:
               return False
       return True


   def clicked(self,num,idx,check): #(all the "updates" in this function refer strictly to the data structures in this program!!!)
       if self.graphics.game_mode=="Friend": #for friend game mode
           self.get_global_board().get_local_list()[idx[0]][num[2] - idx[1]][num[3] - idx[2]] = check #updates the board according to the move that was played
           if self.get_global_board().is_win(self.get_global_board().get_local_list()[idx[0]], check): #checks if a local win ocurred
               self.global_state[idx[3]][idx[4]] = check #updates the global board according to the local win
               self.graphics.local_win(idx[0], check) #passes the sign that won the local board in order to display graphically
               self.graphics.disable_arr.append(idx[0]) #disables the local board that was won
           if self.get_global_board().is_full(self.get_global_board().get_local_list()[idx[0]]) and not self.get_global_board().is_win(self.get_global_board().get_local_list()[idx[0]], check):#if local board was tied/full and not won
               self.global_state[idx[3]][idx[4]]=-1 #updates the global board to refer to the tied local board (tie=-1)
               self.graphics.disable_arr.append(idx[0]) #disables the local board that was tied
           if self.get_global_board().is_win(self.get_global_state(), check): #if a global win ocurred
               self.graphics.win_announcement(check) #display the win graphically
           if self.get_global_board().is_full(self.get_global_state()) and not self.get_global_board().is_win(self.get_global_state(), check): #if a global board is tied/full and not won
               self.graphics.win_announcement(-1) #display the tie graphically
       if self.graphics.game_mode=="Computer": #for computer game mode
           self.get_global_board().local_list[int(num[2]/3)][int(num[3]/3)].get_local()[num[2] - idx[1]][num[3] - idx[2]]=check #updates the board according to the move that was played
           if self.get_global_board().is_win(self.get_global_board().get_local_list()[int(num[2]/3)][int(num[3]/3)].get_local(), check): #if local win ocurred
               self.global_state[idx[3]][idx[4]] = check #updates the global array to display the local win on the global board
               self.graphics.local_win(idx[0], check) #displays the local win graphically
               self.graphics.disable_arr.append(idx[0]) #disables the local board that was won
           if self.get_global_board().is_full(self.get_global_board().get_local_list()[int(num[2]/3)][int(num[3]/3)].get_local()) and not self.get_global_board().is_win(self.get_global_board().get_local_list()[int(num[2]/3)][int(num[3]/3)].get_local(), check):#if a local board is full/tied
               self.global_state[idx[3]][idx[4]]=-1 #update the global array to display the full/tied board
               self.graphics.disable_arr.append(idx[0])# disable the tied global board
           if self.get_global_board().is_win(self.get_global_state(), check):# if global win ocurred
               self.graphics.win_announcement(check)# display global win
           if self.get_global_board().is_full(self.get_global_state()) and not self.get_global_board().is_win(self.get_global_state(), check):# if global tie ocurred (and not global win)
               self.graphics.win_announcement(-1)# display global tie

   def spotlight_func(self,num,idx): #func that finds and creates the spotlight around the legal local board
       #self.spot = self.graphics.get_spotlight_idx(num[2] - idx[1], num[3] - idx[2])
       self.spot=(num[2]-idx[1])+(num[3]-idx[2])*3 #gets the spotlight index (= i + j*3)
       if not self.spot in self.graphics.disable_arr:
           duc = self.graphics.get_winner_text_cord(self.spot)
           spotlight_rect = self.graphics.canvas1.create_rectangle(duc[0], duc[1], duc[0] + 300, duc[1] + 300, fill="",
                                                           outline='red',width=5)
           self.graphics.spot_arr.append(spotlight_rect)
           self.graphics.disable(self.spot)
           self.graphics.enable(self.spot)

       else:
           for i in range(self.graphics.size):
               if not i in self.graphics.disable_arr:
                   self.graphics.enable(i)
                   duc = self.graphics.get_winner_text_cord(i)
                   spotlight_rect = self.graphics.canvas1.create_rectangle(duc[0], duc[1], duc[0] + 300,
                                                                                         duc[1] + 300, fill="",
                                                                                         outline='red',width=5)
                   self.graphics.spot_arr.append(spotlight_rect)




   def get_global_board(self):
       return self.global1

   def get_global_state(self):
       return self.global_state






class Graphics:
   def __init__(self,root,width,height):
       self.width=width
       self.height=height
       self.pre_game()
       self.module=Module(self)
       self.size=9

   def pre_game(self): #func that displays pregame announcements and opening screen
       self.welcome=Label(root,text="Welcome To Ultimate Tic-Tac-Toe!",fg='firebrick4',bg='light blue',font='times 24',height=2)#welcome announcement
       self.welcome.grid(row=0,column=10)
       self.show_rules=Button(root,text="Show Rules",bg='orange',fg='gold',command=self.show_rule_function)#button that shows rules
       self.show_rules.grid(row=1,column=10)
       self.continue_to_game=Button(root,text="Continue",bg='light blue',fg='sandy brown',font='times 14',command=self.continue_to_game_mode)#button that sends to gamemode selection
       self.continue_to_game.grid(row=2,column=10)

   def show_rule_function(self): #displays game rules
       self.welcome.grid_forget() #delete welcome announcement
       self.continue_to_game.grid_remove() #delete continue button
       self.show_rules.grid_remove() #delete show rules button
       #text that displays the rules of the game
       self.rules=Label(text="Rules:\n"
                             "Each small 3x3 tic-tac-toe board is referred to as a local board, \nand the larger 3x3 board is referred to as the global board.\n"
                             "\nThe game starts with X playing wherever they want in any of the 81 empty spots.\n This move sends their opponent to its relative location. "
                             "\nFor example, if X played in the top right square of their local board,\n then O needs to play next in the local board at the top right of the global board.\n"
                             " \nO can then play in any one of the nine available spots in that local board, \neach move sending X to a different local board.\n"
                             "\nIf a move is played so that it is to win a local board by the rules of normal tic-tac-toe, \n"
                             "then the entire local board is marked as a victory for the player in the global board.\n"
                             "\nOnce a local board is won by a player or it is filled completely, no more moves may be played in that board. \n"
                             "If a player is sent to such a board, then that player may play in any other board.\n \nThe game is over when a win occurs in the global board, or if the global board is tied\n",
                        bg='light blue',fg='black',font='times 16')
       self.rules.grid(row=0,column=0)
       self.hide_rules=Button(root,text="Hide Rules",bg='light blue',fg='orange',font='times 14',command=self.hide_rule_function) #button that hides the rules
       self.hide_rules.grid(row=6,column=0)

   def hide_rule_function(self): #hides game rules
       self.hide_rules.grid_remove() #delete hide rules button
       self.rules.grid_forget() #delete rules text
       self.welcome.grid(row=0,column=0) #re-display welcome announcement
       self.continue_to_game.grid(row=2,column=0) #re-dusplay continue button
       self.show_rules.grid(row=1,column=0) #re-display show rules button

   def continue_to_game_mode(self): #game mode selection
       self.welcome.grid_forget() #delete welcome announcement
       self.show_rules.grid_forget() #delete show rules button
       #self.show_rules.grid_forget()
       self.continue_to_game.grid_forget() #delete continue button
       self.play_against=Label(root,text="Choose who to play against (Default is computer) : ",bg='light blue',fg='sandy brown',font='times 18',height=2)#,width=130)
       self.play_against.grid(row=0,column=10)
       self.choose_game_mode=Listbox(root, height=2, selectmode=SINGLE,bg='light blue',font="times 18",fg='chocolate3') #display game mode options
       self.choose_game_mode.insert(1, 'Friend') #first game mode option is against another player
       self.choose_game_mode.insert(2, 'Computer') #second game mode option is against the computer
       self.choose_game_mode.grid(row=1,column=10)
       self.choose_game_mode.select_set(1) #default is against the computer
       self.select_mode=Button(root,text="Select",fg='olive drab',bg='light blue',font='times 18',command=self.choose_first_player)
       self.select_mode.grid(row=2,column=10)

   def choose_first_player(self): #first player selection
       #delete previous screen
       self.play_against.grid_forget()
       self.choose_game_mode.grid_forget()
       self.select_mode.grid_forget()
       self.game_mode = self.choose_game_mode.get(self.choose_game_mode.curselection()[0]) #game mode is whatever the player selected from the options
       self.choose_first=Label(root,text="Choose who goes first: ",bg='light blue',fg='medium orchid',font='times 18',height=1)#,width=130)
       self.choose_first.grid(row=0,column=10)
       self.first_play=Listbox(root,height=2,selectmode=SINGLE,bg='light blue',font='times 18',fg='chocolate3')
       #choose first player if two humans are playing
       if self.game_mode=="Friend":
           text1="X"
           text2="O"
           self.first_play.insert(1, text1)
           self.first_play.insert(2, text2)
           self.first_play.grid(row=1, column=10)
           self.first_play.select_set(0)
           self.select_first = Button(root,text="Select", bg='light blue', fg='chocolate3', font='times 18',
                                      command=self.finalize_starters)  # button that has function that finalizes who the first player is and what the first sign is when playing against computer
           self.select_first.grid(row=2, column=10)
       if self.game_mode=="Computer":
           text1 = "X"
           text2 = "O"
           self.first_play.insert(1, text1)
           self.first_play.insert(2, text2)
           self.first_play.grid(row=1, column=10)
           self.first_play.select_set(0)
           self.select_first = Button(root, text="Select", bg='light blue', fg='chocolate3', font='times 18',
                                      command=self.difficulty_func)
           self.select_first.grid(row=2, column=10)
           #self.display_initial_board()

   def difficulty_func(self): #player chooses difficulty for the game
       self.first=self.first_play.get(self.first_play.curselection()[0])
       self.turns = [self.first, 'O' if self.first == 'X' else 'X']
       self.choose_first.grid_forget()
       self.select_first.grid_forget()
       self.first_play.grid_forget()
       self.difficulty_label=Label(root,text="Choose difficulty: \n(The harder the difficulty \nthe longer the computer's turn is)",bg='light blue', fg='chocolate3', font='times 18')
       self.difficulty_label.grid(row=1,column=10)
       self.difficulty_list=Listbox(root,height=5,selectmode=SINGLE,bg='light blue',font='times 18',fg='chocolate3')
       self.difficulty_list.insert(1, "Easy")
       self.difficulty_list.insert(2, "Medium")
       self.difficulty_list.insert(3, "Hard")
       self.difficulty_list.insert(4, "Master")
       self.difficulty_list.insert(5,"Custom")
       self.difficulty_list.grid(row=2,column=10)
       self.difficulty_list.select_set(0)
       self.difficulty_button=Button(root,text="Select",bg='light blue', fg='chocolate3', font='times 18',command=self.finalize_starters)
       self.difficulty_button.grid(row=3,column=10)


   def finalize_starters(self): #func deletes previous screen and handles difficulty selection
       #delete previous screen
       if self.game_mode=="Friend":
           self.select_first.grid_forget()
           self.first_play.grid_forget()
           self.choose_first.grid_forget()
           self.first = self.first_play.get(self.first_play.curselection()[0])
           self.turns = [self.first, 'O' if self.first == 'X' else 'X'] #decides first player

       if self.game_mode=="Computer":
           self.difficulty_label.grid_forget()
           self.comp_time_str=self.difficulty_list.get(self.difficulty_list.curselection()[0]) #what difficulty was selected?
           if self.comp_time_str=="Easy":
               self.comp_time=0.1
           if self.comp_time_str=="Medium":
               self.comp_time=3
           if self.comp_time_str=="Hard":
               self.comp_time=8
           if self.comp_time_str=="Master":
               self.comp_time=15
           if self.comp_time_str=="Custom":
               self.custom_time() #allows the user to select a custom time
       if (self.game_mode=="Computer" and self.comp_time_str!="Custom") or self.game_mode=="Friend": #for all game modes apart from custom time, continue to next screen
              self.display_initial_board()

   def custom_time(self): #player can choose a custom time for the comp's turn
       self.difficulty_list.grid_forget()
       self.difficulty_button.grid_forget()
       self.time_label=Label(root,text="Enter time",bg='light blue', fg='chocolate3',font='times 18')
       self.time_label.grid(row=0,column=4)
       self.enter_time=Entry(root, bg='light blue',font='times 18')
       self.enter_time.grid(row=2,column=5)
       self.select_time=Button(root,text="Select",bg='light blue', fg='chocolate3',font='times 18', command=self.get_comp_time)
       self.select_time.grid(row=4,column=5)

   def get_comp_time(self): #func that handles the custom time selection
       if self.game_mode=="Computer":
           if self.comp_time_str=="Custom":
               self.comp_time_temp=self.enter_time.get().strip()
               self.comp_time=float(self.comp_time_temp)
               self.time_label.grid_forget()
               self.enter_time.grid_forget()
               self.select_time.grid_forget()
       self.display_initial_board()

   def display_initial_board(self): #deletes previous screen and calls the next function that draws the game board
       if self.game_mode=="Computer":
           self.difficulty_list.grid_forget()
           self.difficulty_button.grid_forget()
       self.draw_outline_board() #function that draws the board skeleton

   def draw_outline_board(self):#function that draws the board skeleton
       self.module.init_golbal(self.game_mode)
       self.skeleton=[]
       self.check=0
       self.indicate_over=0
       self.disable_arr=[]
       self.spot_arr=[]
       self.board_color='Royalblue2'
       self.lines_color=None
       #draws the global tic tac toe board
       #self.canvas1 = Canvas(root, bd=0, highlightthickness=0, bg='gray',height=900,width=900)
       self.canvas1 = Canvas(root, bd=0, highlightthickness=0, bg=self.board_color, height=self.height,width=self.width)
       v1 = self.canvas1.create_line(300, 0, 300, 900, width=5,fill=self.lines_color)
       self.skeleton.append(v1)
       v2 = self.canvas1.create_line(600, 0, 600, 900, width=5,fill=self.lines_color)
       self.skeleton.append(v2)
       h1 = self.canvas1.create_line(0, 300, 900, 300, width=5,fill=self.lines_color)
       self.skeleton.append(h1)
       h2 = self.canvas1.create_line(0, 600, 900, 600, width=5,fill=self.lines_color)
       self.skeleton.append(h2)
       #draws the smaller local boards
       x0=20 #x0 horizontal
       y0=100 #y0 horizontal
       xn=280 #xn horizontal
       yn=100 #yn horizontal
       x01 = 100 #x0 vertical
       y01 = 20 #y0 vertical
       xn1 = 100 #xn vertical
       yn1 = 280 #yn vertical

       for i in range(self.size-1):
           for j in range(int(self.size/3)):
               horiz=self.canvas1.create_line(x0,y0,xn,yn,width=3,fill=self.lines_color)
               self.skeleton.append(horiz)
               x0+=300
               xn+=300
               vert = self.canvas1.create_line(x01, y01, xn1, yn1, width=3,fill=self.lines_color)
               self.skeleton.append(vert)
               y01 += 300
               yn1 += 300

           x0=20
           y0+=100
           xn=280
           yn+=100
           x01 += 100
           y01 = 20
           xn1 += 100
           yn1 = 280

       x0r = 10
       y0r = 10
       xnr = 97
       ynr = 97
       #creates squares that player can click on
       self.rect_arr=[]
       self.xgraphic = []
       self.ygraphic=[]
       for i in range(self.size):
           self.xgraphic.append(x0r)
           self.ygraphic.append(y0r)
           y0r+=100
           x0r+=100
       x0r = 10
       y0r = 10
       for i in range(self.size):
           self.rect_arr.append([])
           for j in range(self.size):
               local_idx = self.get_local_idx(i, j)
               rect = self.canvas1.create_rectangle(x0r, y0r, xnr, ynr, fill=self.board_color,outline=self.board_color)#,state=HIDDEN)
               self.canvas1.tag_bind(rect,"<Button-1>",lambda event, num=[x0r,y0r,i,j,local_idx[0]]:self.on_click(num))
               x0r += 100
               xnr += 100
               self.rect_arr[i].append(rect)
           x0r = 10
           y0r += 100
           xnr = 97
           ynr += 100
       #self.initial_canvas_x=0#200
       self.initial_canvas_x=200
       self.canvas1.place(x=self.initial_canvas_x,y=0)
       self.new_game_button=Button(root,text='New Game',command= self.new_game)
       self.new_game_button.place(x=905+self.initial_canvas_x,y=870)
       self.restart_button=Button(root,text="Restart",command=self.restart_game)
       self.restart_button.place(x=905+self.initial_canvas_x,y=800)

       if self.game_mode=="Computer":
           root.update()
           self.comp_game()
           root.update()
           #None

   def restart_game(self): #func that restarts the current game with the same settings
       self.canvas1.place_forget()
       self.new_game_button.place_forget()
       self.restart_button.place_forget()
       self.module = Module(self)
       self.size = 9
       self.display_initial_board()

   def get_local_idx(self, i, j): #func that recieves a coordinate and returns an array conataining it's local idx and it's local coordinate
       iminus = int(i/3)*3
       jiminus =int(j/3)*3
       local_idx1 = int(i/3)+int(j/3)*3
       local_cord = [int(i/3), int(j/3)]
       return [local_idx1, iminus, jiminus, local_cord[0], local_cord[1]]


   def disable(self,idx): #func that disables all of the local boards except the one it recieves
       for i in range(self.size):
           for j in range(self.size):
               if idx!=self.get_local_idx(i,j)[0]:
                   self.canvas1.itemconfigure(self.rect_arr[i][j],state=DISABLED,fill=self.board_color)

   def enable(self,idx): #func that enables a specific local board
       for i in range(self.size):
           for j in range(self.size):
               if idx==self.get_local_idx(i,j)[0]  and idx not in self.disable_arr:
                   self.canvas1.itemconfigure(self.rect_arr[i][j],state=NORMAL,fill=self.board_color)

   def comp_game(self,prevMove=None): #func that is in charge of the comp's turn, passes relevant parameters (move, symbol) and calls mcts
       if self.indicate_over==-1: #check if game ended
           return
       if self.check>=1: #if first turn already ocurred
           while(len(self.spot_arr)>0): #takes care of deleting the current spotlight in favor of the new one
               self.canvas1.delete(self.spot_arr[0])
               self.spot_arr.remove(self.spot_arr[0])
       board= self.module.global1 #create global board
       text1=self.turns[self.check%2] #computer's sign
       p1=MCTS(text1,compTime=self.comp_time) #create the mcts object

       self.check+=1 #next turn
       move = None #current move
       validMoves = board.getValidMoves(prevMove)[0] #gets all valid moves to play
       while move not in validMoves:
           move=p1.getMove(deepcopy(board),prevMove)#selects the move to play

       board.playMove(move, text1) #plays the comp's turn
       text=self.canvas1.create_text(self.ygraphic[move[1]]+40,self.xgraphic[move[0]]+40,font='times 48',text=text1) #displays the comp's turn
       idx=self.get_local_idx(move[0],move[1]) #gets the local idx of the coordinates of the move that was played
       self.module.clicked([0,0,move[0],move[1],0],idx,text1) #passes the comp's turn over to the module to check for wins/ties/legality of moves
       self.module.spotlight_func([0,0,move[0],move[1],0],idx) #calls the function that updates the spotlight


   def on_click(self,num): #func that handles the human players turn (once a click ocurred), passes relevant parameters to module class to update the data board and check for win/draw
       if self.indicate_over==-1: #check if game ended
           return
       if self.check>=1:#if first turn already ocurred
           while(len(self.spot_arr)>0):#takes care of deleting the current spotlight in favor of the new one
               self.canvas1.delete(self.spot_arr[0])
               self.spot_arr.remove(self.spot_arr[0])

       idx=self.get_local_idx(num[2],num[3]) #gets local index of the move to be played
       text1=self.turns[self.check%2] #gets the sign to display in the current turn (X or O)
       self.check+=1 #next turn

       if not self.module.legal_click(num,idx): #if the click wasn't legal, redo current turn
           self.check-=2
           return

       text=self.canvas1.create_text(num[0]+40,num[1]+40,font='times 48',text=text1) #displays the turn (X or O)
       if text1=="X":
           check=1
       if text1=="O":
           check=2
       if text1=="?":
           check=0
       if self.game_mode=="Friend":
           self.module.clicked(num,idx,check) #passes the turn parameters to the module class to check legality and if a win/tie ocurred
           self.module.spotlight_func(num,idx) #calls the spotlight function
       if self.game_mode=="Computer":
           self.module.clicked(num, idx, text1) #passes the turn parameters to the module class to check legality and if a win/loss/tie ocurred
           root.update()
           self.module.spotlight_func(num, idx) #calls the spotlight function
           root.update()
           self.comp_game([num[2],num[3]]) #passes the turn to the computer
           root.update()



   def win_announcement(self,check):#func that announces the game winner
       if self.game_mode=="Friend":
           if check == 1:
               text = 'X'+' Wins!'
           if check == 2:
               text = "O"+" Wins!"
           if check==-1 or check=="?":
               text='Tie'
       if self.game_mode=="Computer":
           if check=="?" or check==-1:
               text="Tie"
           else:
               text=check+ "Wins"

       self.disable(9)
       self.indicate_over = -1
       self.canvas1.create_text(500, 500, font='times 200', text=text , fill='red')
       return


   def get_winner_text_cord(self,local_idx):#func that recieves a local index and returns the coordinate that matches it in order to display the local winner
       x0_text=int(local_idx/3)*300
       y0_text=int(local_idx%3)*300
       return [x0_text,y0_text]

   def local_win(self,local_idx,winner):#func that displays the local winner on a local board that has been won
       if winner==1:
           win_text="X"
       if winner==2:
           win_text="O"
       if self.game_mode=="Computer":
           win_text=winner
       win_cord=self.get_winner_text_cord(local_idx)
       win=self.canvas1.create_text(win_cord[0]+150,win_cord[1]+150,font='times 250',fill='pink',text=win_text)


   def new_game(self): #func that deletes the current board and restarts the game
       self.canvas1.place_forget()
       self.new_game_button.place_forget()
       self.restart_button.place_forget()
       self.module = Module(self)
       self.size = 9
       self.pre_game()

root = Tk()
width, height = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("{0}x{1}+0+0".format(width,height))
width-=430
Graphics(root,width,height)
root.config(bg='light blue')
root.attributes('-fullscreen', True)
root.mainloop()


