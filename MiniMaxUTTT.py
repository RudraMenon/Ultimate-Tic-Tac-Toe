import copy, math, statistics
from time import time


class Board:
    # define 9x9 matrix. each array is a 'box'. 9 boxes make a board
    # each row is a game of tic tac toe. 
    # ex [1,2,3,4,5,6,7,8,9]
    #1|2|3
    #4|5|6
    #7|8|9
    board = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0]]

    # list of indexes (row,col) that one player can occupy to win
    winLines = [[(r, c) for c in range(3)] for r in range(3)] + [[(r, c) for r in range(3)] for c in range(3)] + [[
        (i, i) for i in range(3)]] + [[(i, 2 - i) for i in range(3)]]

    # deepcopy board to simulate moves
    def copyBoard(self, oldboard):
        self.board = copy.deepcopy(oldboard.board)

       
    # return winner of a game of Tic Tac Toe
    def TTTWinner(self, box):
        for line in self.winLines:
            # convert list of coordinates (row, col) to one index
            # ex [(2,2)] -> [5]
            actLine = [box[s[0] * 3 + s[1]] for s in line]
            if actLine[0] != 0 and actLine.count(actLine[0]) == len(actLine):
                return actLine[0]
        return 0

    def boxWinner(self, boxInd):
        # return the winner of a box with given box number (0-9)
        return self.TTTWinner(self.board[boxInd])

    def gameWinner(self):
        # return winner of game, 0 if none, -1 if tie
        gW = self.TTTWinner([self.boxWinner(i) for i in range(9)])
        if gW != 0:
            return gW
        for i in range(9):
            if self.boxWinner(i) == 0 and self.getOptions(i):
                return 0
        return -1

    def prtBoard(self, boxN=4):
        # print board to console
        print("------------------------")
        for bigRow in range(3):
            for smallRow in range(3):
                line = ""
                for bigCol in range(3):
                    for smallCol in range(3):
                        if smallCol == 0:
                            if bigRow * 3 + bigCol == boxN:
                                line += ">"
                            else:
                                line += " "
                        line = line + str(self.board[bigRow * 3 + bigCol][smallRow * 3 + smallCol]) + " "
                    line = line + "|"

                line = line.replace('0', " ")
                line = line.replace('1', "O")
                line = line.replace('2', "X")
                print(line)
            print("------------------------")

    def fromPrintedString(self, s):
        # for testing and debugging 
        # copy and paste board exactly as printed and pass as 's'
        s = s.replace("X", "1")
        s = s.replace("O", "2")
        s = s.replace(">", " ")
        while "   " in s:
            s = s.replace("   ", " 0 ")
        lines = s.splitlines()
        leftBox = 0
        leftSpot = -3
        for i, line in enumerate(lines):
            boxN = leftBox
            leftSpot += 3
            spot = leftSpot
            if line[0] == "-":
                leftBox = leftBox + 3
                leftSpot = -3
            # for spot in line.split(" ")
            else:
                for x in line.split(" "):
                    if x:
                        if x == "|":
                            boxN += 1
                            spot = leftSpot
                        else:
                            self.board[boxN][spot] = int(x)
                            spot += 1

    def setSpot(self, box, spot, num):
        # set spot on board to player number
        self.board[box][spot] = num

    def getOptions(self, boxN):
        # return a list of available spots in a box
        return [i for i, x in enumerate(self.board[boxN]) if x == 0]

    def guessSpotOrder(self, boxN, predictMoves, depth):
        # guess the best spot in a box to improve alpha beta pruning
        options = self.getOptions(boxN)
        optRank = {}
        box = self.board[boxN]
        for spot in options:
            optRank[spot] = 0
            if self.boxWinner(spot) != 0:
                optRank[spot] = 10
            else:
                optRank[spot] = - 10

        for line in self.winLines:
            actLine = [box[s[0] * 3 + s[1]] for s in line]
            if (actLine.count(1) == 2 or actLine.count(2) == 2) and actLine.count(0) == 1:
                s = line[actLine.index(0)]
                spot = s[0] * 3 + s[1]
                optRank[spot] = optRank[spot] - 2
        # look at most recent predictions to improve guess

        return list({k: v for k, v in sorted(optRank.items(), key=lambda item: item[1])}.keys())

    def toString(self, n, p):
        s = ""
        for line in self.board:
            for spot in line:
                s = s + " " + str(spot)
        return str(n) + " " + str(p) + " " + s



def updatePlayer():
    global player
    player = otherPlayer(player)


def otherPlayer(player):
    if player == 1:
        return 2
    else:
        return 1


def getPlayerInput(boxN):
    global player
    options = board.getOptions(boxN)
    keypad = [0, 6, 7, 8, 3, 4, 5, 0, 1, 2]
    while not options or board.boxWinner(boxN) != 0 and boxN in range(9):
        boxN = keypad[int(input("Pick a Box"))]
        options = board.getOptions(boxN)

    print("Player " + str(player))
    spot = -1
    while spot not in options:
        try:
            spot = keypad[int(input("Please select from: " + str(board.getOptions(boxN))))]
        except:
            print("that aint it")
    return [boxN, spot]



class aiPlayer:
    maxDepth = 4
    minMaxVals = {"boxWin": 25, "gameWin": 2000000, "gameTie": 1000000}
    playerNum = 0
    predictMoves = []

    def __init__(self, playerNum, boxWin):
        self.playerNum = playerNum
        self.minMaxVals["boxWin"] = boxWin

    def play(self, board, boxN):
        # decide best move and place it
        
        # if this specific boxes does not have any options, loop through other boxes
        if board.boxWinner(boxN) != 0 or not board.getOptions(boxN):
            bestMove = -1
            bestRating = -10000000000
            for boxI in range(9):
                if board.boxWinner(boxI) == 0 and board.getOptions(boxI):
                    thisBoardMove = self.play(board, boxI)
                    if thisBoardMove[2][0] > bestRating:
                        bestRating = thisBoardMove[2][0]
                        boxN = boxI
                        bestMove = thisBoardMove[1]
            return [boxN, bestMove, bestRating]

        hypBoard = Board()
        hypBoard.copyBoard(board)

        totalstart = time()
        myBestMoves = self.boxRating(boxN, hypBoard, -1000000000, 1000000000)

        options = hypBoard.getOptions(boxN)
        bestMove = options[0]
        for spot in options:
            if myBestMoves[spot][0] > myBestMoves[bestMove][0]:
                bestMove = spot

        self.predictMoves = myBestMoves[bestMove][1][2:]

        print("best path is ", myBestMoves[bestMove][1], myBestMoves[bestMove][0])
        # oppBestMoves = moveRating(boxN, otherPlayer(player), hypBoard, 0)
        print("My Best Moves as " + str(self.playerNum))

        print("Bot Moves: " + str(bestMove) + "in " + str(time() - totalstart))
        return [boxN, bestMove, myBestMoves[bestMove]]

    def qualifyBoard(self, cBoard):
        # check each box and evaluate who is winning
        # I evaluate a box by counting the # of win cases that are still 
        # possible for one player and subtracting the # of opponent's possible win cases
        boxRatings = [0] * 9
        for boxN in range(9):
            boxWinner = cBoard.boxWinner(boxN)
            if boxWinner == self.playerNum:
                boxRatings[boxN] = self.minMaxVals["boxWin"]
            elif boxWinner == otherPlayer(self.playerNum):
                boxRatings[boxN] = -1 * self.minMaxVals["boxWin"]
            else:
                box = cBoard.board[boxN]
                for line in cBoard.winLines:
                    actLine = [box[s[0] * 3 + s[1]] for s in line]
                    for spot in actLine:
                        if spot == self.playerNum:
                            boxRatings[boxN] = boxRatings[boxN] + 1
                        if spot == otherPlayer(self.playerNum):
                            boxRatings[boxN] = boxRatings[boxN] - 1

        return boxRatings

    predictTime = [0, 0]

    def naiveWinPredict(self, cBoard):
        st = time()
        gameWinner = cBoard.gameWinner()
        if gameWinner != 0:
            if gameWinner == -1:
                return self.minMaxVals["gameTie"]
            if gameWinner == self.playerNum:
                return self.minMaxVals["gameWin"]
            return self.minMaxVals["gameWin"] * -1
        pRating = self.qualifyBoard(cBoard)

        normalBoard = [pRating[i] / self.minMaxVals["boxWin"] for i in range(9)]
        winRating = 0.0

        for line in cBoard.winLines:
            actLine = [normalBoard[s[0] * 3 + s[1]] for s in line]
            for spot in actLine:
                winRating = winRating + spot

        self.predictTime[0] = 1
        self.predictTime[1] = time() - st

        return winRating

    def boxRating(self, boxN, hypBoard, a, b):
        allMoves = [0] * 9
        options = hypBoard.guessSpotOrder(boxN, self.predictMoves, 0)
        for spot in options:
            st = time()
            hypBoard.setSpot(boxN, spot, self.playerNum)
            bestPath = self.moveRating(spot, otherPlayer(self.playerNum), hypBoard, 0, a, b)
            allMoves[spot] = [bestPath[0], [(boxN, spot)] + bestPath[1]]
            hypBoard.setSpot(boxN, spot, 0)

            # a = max(a, bestPath[0])
        print(self.c, self.nc)
        return allMoves

    previouslyCrunched = {}
    bigDepth = 4
    c = 0
    nc = 0

    def moveRating(self, boxN, player, cpyBoard, depth, a, b):
        gW = cpyBoard.gameWinner()
        if gW != 0:
            if gW == self.playerNum:
                return [self.minMaxVals["gameWin"], ["won"]]
            else:
                return [-1 * self.minMaxVals["gameWin"], ["lost"]]

        maxPlayer = self.playerNum == player
        hypBoard = Board()
        hypBoard.copyBoard(cpyBoard)
        if depth > self.maxDepth:
            prediction = self.naiveWinPredict(cpyBoard)
            return [prediction, ['end']]
        if hypBoard.boxWinner(boxN) != 0:
            boxes = [box for box in range(9) if hypBoard.boxWinner(box) == 0]
        else:
            boxes = [boxN]
        value = [-1000000000] if maxPlayer else [1000000000]
        bestSpot = -1
        bestBox = -1
        for boxN in boxes:
            options = hypBoard.guessSpotOrder(boxN, self.predictMoves, depth)
            # options = hypBoard.getOptions(boxN)
            for spot in options:
                hypBoard.setSpot(boxN, spot, player)
                if maxPlayer:
                    temp = self.moveRating(spot, otherPlayer(player), hypBoard, depth + 1, a, b)
                    if temp[0] > value[0]:
                        value = temp
                        bestSpot = spot
                        bestBox = boxN
                    a = max(a, value[0])
                else:
                    temp = self.moveRating(spot, otherPlayer(player), hypBoard, depth + 1, a, b)

                    if temp[0] < value[0]:
                        value = temp
                        bestSpot = spot
                        bestBox = boxN

                    b = min(b, value[0])
                hypBoard.setSpot(boxN, spot, 0)
                if a >= b:
                    self.c = self.c + 1
                    break
                self.nc = self.nc + 1
        if len(value) < 2:
            return [value[0], [(player, bestBox, bestSpot)]]
        return [value[0], [(player, bestBox, bestSpot)] + value[1]]


#
board = Board()

players = []
ai1 = aiPlayer(1,25)
ai2 = aiPlayer(2,25)
players = [ai1, ai2]

player = 2


def playGame():
    global player, players
    boxN = 4
    print("Player input looks like a keypad")
    print("example")
    print("|7|8|9|\n|4|5|6|\n|1|2|3|")
    while board.gameWinner() == 0:
        ai = players[player - 1]
        [boxN, spot, rating] = ai.play(board, boxN)

        # [boxN, spot, rating] = ai2.play(board, boxN)
        board.setSpot(boxN, spot, player)
        board.prtBoard(boxN)
        updatePlayer()
        boxN = spot

        
        [boxN, spot] = getPlayerInput(boxN)
        board.setSpot(boxN, spot, player)
        board.prtBoard(boxN)
        updatePlayer()
        boxN = spot

    print("player " + str(board.gameWinner()) + " won!!!")

    print(ai1.c/ai1.nc)
    print(ai2.c/ai2.nc)


s = """      O | X O   |   X   |
   X   | X O   | O     |
 X O   |   O   | X X X |
------------------------
>X X O | O X O | O     |
>O   O | X X X | O   X |
>X     |       | O X   |
------------------------
   O X |     O | X     |
   O   | X O X |     O |
   O X | O X   |     O |"""
# board.fromPrintedString(s)
# board.prtBoard()



#
# board.setSpot(2,5,1)
# ai2.play(board,5)


def timeFunction(f):
    st = time()
    f()
    print("function finished in:", time() - st)

timeFunction(playGame)
#341.8966062068939
#445
