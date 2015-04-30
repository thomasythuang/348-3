#!/usr/bin/env python
import struct, string, math, time
from copy import *

class SudokuBoard:
    """This will be the sudoku board game object your player will manipulate."""
  
    def __init__(self, size, board):
      """the constructor for the SudokuBoard"""
      self.BoardSize = size #the size of the board
      self.CurrentGameBoard= board #the current state of the game board
      #a 2-d array of legal moves for each possible board space
      self.legalMoves = [[[k+1 for k in range(size)] for i in range(size)] for j in range(size)]

    def set_value(self, row, col, value):
        """This function will create a new sudoku board object with the input
        value placed on the GameBoard row and col are both zero-indexed"""

        #add the value to the appropriate position on the board
        self.CurrentGameBoard[row][col]=value
        #return a new board of the same size with the value added
        return SudokuBoard(self.BoardSize, self.CurrentGameBoard)
                                                                                                                 
    def print_board(self):
        """Prints the current game board. Leaves unassigned spots blank."""
        div = int(math.sqrt(self.BoardSize))
        dash = ""
        space = ""
        line = "+"
        sep = "|"
        for i in range(div):
            dash += "----"
            space += "    "
        for i in range(div):
            line += dash + "+"
            sep += space + "|"
        for i in range(-1, self.BoardSize):
            if i != -1:
                print "|",
                for j in range(self.BoardSize):
                    if self.CurrentGameBoard[i][j] > 9:
                        print self.CurrentGameBoard[i][j],
                    elif self.CurrentGameBoard[i][j] > 0:
                        print "", self.CurrentGameBoard[i][j],
                    else:
                        print "  ",
                    if (j+1 != self.BoardSize):
                        if ((j+1)//div != j/div):
                            print "|",
                        else:
                            print "",
                    else:
                        print "|"
            if ((i+1)//div != i/div):
                print line
            else:
                print sep

def parse_file(filename):
    """Parses a sudoku text file into a BoardSize, and a 2d array which holds
    the value of each cell. Array elements holding a 0 are considered to be
    empty."""

    f = open(filename, 'r')
    BoardSize = int( f.readline())
    NumVals = int(f.readline())

    #initialize a blank board
    board= [ [ 0 for i in range(BoardSize) ] for j in range(BoardSize) ]

    #populate the board with initial values
    for i in range(NumVals):
        line = f.readline()
        chars = line.split()
        row = int(chars[0])
        col = int(chars[1])
        val = int(chars[2])
        board[row-1][col-1]=val
    
    return board
    
def is_complete(sudoku_board):
    """Takes in a sudoku board and tests to see if it has been filled in
    correctly."""
    BoardArray = sudoku_board.CurrentGameBoard
    size = len(BoardArray)
    subsquare = int(math.sqrt(size))

    #check each cell on the board for a 0, or if the value of the cell
    #is present elsewhere within the same row, column, or square
    for row in range(size):
        for col in range(size):
            if BoardArray[row][col]==0:
                return False
            for i in range(size):
                if ((BoardArray[row][i] == BoardArray[row][col]) and i != col):
                    return False
                if ((BoardArray[i][col] == BoardArray[row][col]) and i != row):
                    return False
            #determine which square the cell is in
            SquareRow = row // subsquare
            SquareCol = col // subsquare
            for i in range(subsquare):
                for j in range(subsquare):
                    if((BoardArray[SquareRow*subsquare+i][SquareCol*subsquare+j]
                            == BoardArray[row][col])
                        and (SquareRow*subsquare + i != row)
                        and (SquareCol*subsquare + j != col)):
                            return False
    return True

def init_board(file_name):
    """Creates a SudokuBoard object initialized with values from a text file"""
    board = parse_file(file_name)
    sb = SudokuBoard(len(board), board)

    #when the board is initialized with starting numbers,
    #remove the potential values that they already eliminate
    for row in range(sb.BoardSize):
    	for col in range(sb.BoardSize):
    		removeMoves(sb, row, col, sb.CurrentGameBoard[row][col])

    return sb

def solve(initial_board, forward_checking = False, MRV = False, MCV = False,
    LCV = False):
    """Takes an initial SudokuBoard and solves it using back tracking, and zero
    or more of the heuristics and constraint propagation methods (determined by
    arguments). Returns the resulting board solution. """

    board = initial_board

    # If the puzzle is complete, return!
    if is_complete(board):
    	return board

    # Get the position of an open space on the board
    row, col = findOpenSpace(board, MRV, MCV)
    # Get the list of legal moves for that spot
    if forward_checking:
    	nums = board.legalMoves[row][col]
    	
    	# Sort the moves based on the least constraining values
    	if LCV:
    		nums = findConstraints(board, row, col, nums)

    # If no forward checking, just use 1-9
    else:
    	nums = range(board.BoardSize)
    	nums = [x+1 for x in nums]

    # Try a value and backtrack if it doesn't work out
    for n in nums:
    	nb = deepcopy(board)
    	if checkRow(nb, row, n) and checkColumn(nb, col, n) and checkSmallBox(nb, row, col, n):
    		nb.set_value(row, col, n)
    		removeMoves(nb, row, col, n)
    		res = solve(nb, forward_checking, MRV, MCV, LCV)
    		if res:
    			return res
    return False

def findOpenSpace(board, MRV, MCV):
	"""Finds an open space in a board and returns its coordinates"""
	size = board.BoardSize
	gb = board.CurrentGameBoard
	
	# MRV (If MRV and MCV are both selected, MRV will be selected by default)
	if MRV:
		minVal = size # The least amount of values remaining for a variable
		for row in range(size):
			for col in range(size):
				if (gb[row][col] == 0):
					# If this spot has less values than the min, it's the new min
					if len(board.legalMoves[row][col]) < minVal:
						minVal = len(board.legalMoves[row][col])
						minRow = row
						minCol = col
		return minRow, minCol
	# MCV
	elif MCV:
		maxCon = 0 # The most constraints with other variables
		for row in range(size):
			for col in range(size):
				if (gb[row][col] == 0):
					# If this spot has more constraints than the max, it's the new max
					con = countConstraints(board, row, col)
					if con > maxCon:
						maxCon = con
						maxRow = row
						maxCol = col
		return maxRow, maxCol
	else: 
		# If no MRV or MCV, choose the most top-left open space
		for row in range(size):
			for col in range(size):
				if (gb[row][col] == 0):
					return row, col

	return False

def findConstraints(board, rowNum, colNum, moves):
	"""Finds how many choices a value affects for LCV"""
	# List to keep track of how many choices a move affects
	constraints = [0]*len(moves)

	size = int(math.sqrt(board.BoardSize))

	# Set rowIndex and colIndex to the top left of the appropriate small box
	for n in range(size):
		if (rowNum < ((n+1) * size)):
			rowIndex = n * size
			break
	for n in range(size):
		if (colNum < ((n+1) * size)):
			colIndex = n * size
			break

	# Track affected vertical & horizontal spaces
	for move in moves:
		for i in range(board.BoardSize):
			if move in board.legalMoves[i][colNum]:
				constraints[moves.index(move)] += 1
			if move in board.legalMoves[rowNum][i]:
				constraints[moves.index(move)] += 1

		# Track affected spaces in the same small square
		for row in range(size):
			for col in range(size):
				if (rowIndex+row != rowNum) and (colIndex+col != colNum):
					if move in board.legalMoves[rowIndex+row][colIndex+col]:
						constraints[moves.index(move)] += 1

	# Sort the moves by the least amount of constraints on other variables
	newMoves = [x for (y,x) in sorted(zip(constraints, moves))]
	return newMoves

def countConstraints(board, rowNum, colNum):
	"""Counts how many constraints a variable is involved in with other variables"""
	
	gb = board.CurrentGameBoard
	constraints = 0

	# Count empty spaces in the same row or column
	for i in range(board.BoardSize):
		if gb[i][colNum] == 0:
			constraints += 1
		if gb[rowNum][i] == 0:
			constraints += 1

	size = int(math.sqrt(board.BoardSize))

	# Set rowIndex and colIndex to the top left of the appropriate small box
	for n in range(size):
		if (rowNum < ((n+1) * size)):
			rowIndex = n * size
			break
	for n in range(size):
		if (colNum < ((n+1) * size)):
			colIndex = n * size
			break

	# Count empty spaces in the same small square
	for row in range(size):
		for col in range(size):
			if (rowIndex+row != rowNum) and (colIndex+col != colNum):
				if gb[rowIndex+row][colIndex+col] == 0:
					constraints += 1
	return constraints

def removeMoves(board, rowNum, colNum, val):
	"""Removes the given value from the eligible moves for any spaces
	in the same row, column, or small square"""

	# Remove the value from the legal moves in the same row/column
	for i in range(board.BoardSize):
		if val in board.legalMoves[i][colNum]:
			board.legalMoves[i][colNum].remove(val)
		if val in board.legalMoves[rowNum][i]:
			board.legalMoves[rowNum][i].remove(val)

	size = int(math.sqrt(board.BoardSize))

	# Set rowIndex and colIndex to the top left of the appropriate small box
	for n in range(size):
		if (rowNum < ((n+1) * size)):
			rowIndex = n * size
			break
	for n in range(size):
		if (colNum < ((n+1) * size)):
			colIndex = n * size
			break

	# Remove the value from the legal moves in the same small square
	for row in range(size):
		for col in range(size):
			if val in board.legalMoves[rowIndex+row][colIndex+col]:
				board.legalMoves[rowIndex+row][colIndex+col].remove(val)

def checkRow(board, rowNum, val):
	"""Checks a row for the given value and returns false if it exists"""

	for i in board.CurrentGameBoard[rowNum]:
		if (i == val):
			return False

	return True

def checkColumn(board, colNum, val):
	"""Checks a row for the given value and returns false if it exists"""

	for row in board.CurrentGameBoard:
		if (row[colNum] == val):
			return False

	return True

def checkSmallBox(board, rowNum, colNum, val):
	"""Checks a small square for the given value and returns false if it exists"""

	gb = board.CurrentGameBoard
	size = int(math.sqrt(board.BoardSize))

	# Set rowIndex and colIndex to the top left of the appropriate small box
	for n in range(size):
		if (rowNum < ((n+1) * size)):
			rowIndex = n * size
			break
	for n in range(size):
		if (colNum < ((n+1) * size)):
			colIndex = n * size
			break

	# Check the small box for the value
	for row in range(size):
		for col in range(size):
			if (gb[rowIndex+row][colIndex+col] == val):
				return False

	return True

def test():

	#path1 = '4_4.sudoku'
	#path2 = '9_9.sudoku'
	path1 = 'input_puzzles/more/9x9/9x9.3.sudoku'
	path2 = 'input_puzzles/more/9x9/9x9.7.sudoku'

	b = init_board(path1)
	b.print_board()
	#t0 = time.clock()
	b2 = solve(b, True, True, False, False)
	#print "4x4:", time.clock() - t0, "sec"
	b2.print_board()

	bb = init_board(path2)
	bb.print_board()
	#t1 = time.clock()
	bb2 = solve(bb, True, True, False, False)
	#print "9x9:", time.clock() - t1, "sec"
	bb2.print_board()
	"""
	bbb = init_board('16_16.sudoku')
	#bbb.print_board()
	t2 = time.clock()
	bbb2 = solve(bbb, True, False, False, True)
	#print "16x16:", time.clock() - t2, "sec"
	#bbb2.print_board() 
	"""