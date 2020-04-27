import copy, math, statistics
from time import time


class Board:
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

    winLines = [[(r, c) for c in range(3)] for r in range(3)] + [[(r, c) for r in range(3)] for c in range(3)] + [[
        (i, i) for i in range(3)]] + [[(i, 2 - i) for i in range(3)]]

    def copyBoard(self, oldboard):
        self.board = copy.deepcopy(oldboard.board)

    def getBox(self, boxN):
        return self.board[boxN]

    def TTTWinner(self, box):
        for line in self.winLines:
            actLine = [box[s[0] * 3 + s[1]] for s in line]
            if actLine[0] != 0 and actLine.count(actLine[0]) == len(actLine):
                return actLine[0]
        return 0

    def boxWinner(self, boxInd):
        return self.TTTWinner(self.board[boxInd])

    def gameWinner(self):
        return self.TTTWinner([self.boxWinner(i) for i in range(9)])

    def prtBoard(self, boxN=4):
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

    def setSpot(self, box, spot, num):
        self.board[box][spot] = num

    def getOptions(self, boxN):
        return [i for i, x in enumerate(self.board[boxN]) if x == 0]

    def guessSpotOrder(self, boxN):
        options = self.getOptions(boxN)
        optRank = {}
        box = self.getBox(boxN)
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

        return list({k: v for k, v in sorted(optRank.items(), key=lambda item: item[1])}.keys())


    def qualifyBoard(self, player):
        boxRatings = [0] * 9
        for boxN in range(9):
            boxWinner = self.boxWinner(boxN)
            if boxWinner == player:
                boxRatings[boxN] = players[player - 1].minMaxVals["boxWin"]
            elif boxWinner == otherPlayer(player):
                boxRatings[boxN] = -1 * players[player - 1].minMaxVals["boxWin"]
            else:
                box = self.getBox(boxN)
                for line in self.winLines:
                    actLine = [box[s[0] * 3 + s[1]] for s in line]
                    for spot in actLine:
                        if spot == player:
                            boxRatings[boxN] = boxRatings[boxN] + 1
                        if spot == otherPlayer(player):
                            boxRatings[boxN] = boxRatings[boxN] - 1

        return boxRatings

    predictTime = [0,0]
    def naiveWinPredict(self, player, a=False):
        st = time()

        gameWinner = self.gameWinner()
        if gameWinner != 0:
            if gameWinner == player:
                return players[player - 1].minMaxVals["gameWin"]
            return players[player - 1].minMaxVals["gameWin"] * -1
        pRating = self.qualifyBoard(player)
        adjustRating = copy.deepcopy(pRating)
        for boxN in range(9):
            if self.boxWinner(boxN) == 0:
                options = self.getOptions(boxN)
                cloBoxN = max(1, len([x for x in options if self.boxWinner(x) != 0]))

                for spot in [x for x in range(9) if x not in options]:
                    adjustRating[boxN] = adjustRating[boxN] + pRating[spot] * cloBoxN * players[player - 1].minMaxVals["sendBoxRating"]

        normalBoard = [adjustRating[i] / players[player - 1].minMaxVals["boxWin"] for i in range(9)]
        winRating = 0.0

        for line in self.winLines:
            actLine = [normalBoard[s[0] * 3 + s[1]] for s in line]
            for spot in actLine:
                winRating = winRating + spot
        #
        if a:
            print(pRating)
            print(adjustRating)
            print(normalBoard)
        self.predictTime[0] += 1
        self.predictTime[1] += time()-st

        return winRating

    def toString(self, n, p):
        s = ""
        for line in self.board:
            for spot in line:
                s = s + " " + str(spot)
        return str(n) + " " + str(p) + " " + s

    def fromString(self, s):
        s = [int(x) for x in s.split("  ")[1].split(" ")]
        for i in range(9):
            self.board[i] = s[i * 9:i * 9 + 9]


boardLookup = {}

# return a number on an arbitrary scale representing how
#    much better it is for a player to be allowed
#    to play in a certain box
# si = -1000000000000
# spotRating = {0: si, 1: si, 2: si, 3: si, 4: si, 5: si, 6: si, 7: si, 8: si}
#
# # NEED TO UPDATE RULES-----------------------
# if hypBoard.boxWinner(boxN) != 0:
#     return spotRating
#
# cpyBoard = Board()
# cpyBoard.copyBoard(hypBoard)
#
# options = cpyBoard.getOptions(boxN)
#
# if not options:
#     return spotRating
#
# for spot in options:
#     cpyBoard.setSpot(boxN, spot, player)
#     if (cpyBoard.boxWinner(spot) == 0):
#         nextBoxRating = boxRating(spot, otherPlayer(player), cpyBoard, depth + 1, maxPlayer, a, b)
#     else:
#         maxBox = boxRating(0, otherPlayer(player), cpyBoard, depth + 1, maxPlayer, a, b)
#         for i in range(1, 9):
#             if cpyBoard.boxWinner(i) == 0:
#                 maxBox = max(maxBox, boxRating(i, otherPlayer(player), cpyBoard, depth + 1, maxPlayer, a, b))
#         nextBoxRating = maxBox
#
#     spotRating[spot] = nextBoxRating
#     cpyBoard.setSpot(boxN, spot, 0)
#     if maxPlayer == player:
#         a = max(a, spotRating[spot])
#     else:
#         b = min(b, spotRating[spot])
#     if a >= b:
#         return spotRating
#
# return spotRating


player = 1
board = Board()


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


# minMaxDict = {"stwo": 1, "sthree": 10, "btwo"}

class aiPlayer:
    maxDepth = 4
    minMaxVals = {"boxWin": 25, "gameWin": 2000000, "sendBoxRating": 0.2}

    def play(self, player, board, boxN):
        if board.boxWinner(boxN) != 0 or not board.getOptions(boxN):
            bestMove = -1
            bestRating = -10000000000
            for i in range(9):
                if board.boxWinner(i) == 0 and board.getOptions(boxN):
                    thisBoardMove = self.play(player, board, i)
                    print("box", i)
                    if thisBoardMove[2] > bestRating:
                        bestRating = thisBoardMove[2]
                        boxN = i
                        bestMove = thisBoardMove[1]
            print([boxN, bestMove, bestRating])
            return [boxN, bestMove, bestRating]

        hypBoard = Board()
        hypBoard.copyBoard(board)

        totalstart = time()
        myBestMoves = self.boxRating(boxN, player, hypBoard, -1000000000, 1000000000)
        options = hypBoard.getOptions(boxN)
        bestMove = options[0]
        for spot in options:
            if myBestMoves[spot] > myBestMoves[bestMove]:
                bestMove = spot
        print("avg predict time:", board.predictTime[1]/board.predictTime[0])

        # oppBestMoves = moveRating(boxN, otherPlayer(player), hypBoard, 0)
        print("My Best Moves as " + str(player) + " is " + str([myBestMoves[x] for x in range(9)]))

        print("Bot Moves: " + str(bestMove) + "in " + str(time() - totalstart))
        # print("Opp Best Moves" + str([round(oppBestMoves[x], 2) for x in range(9)]))
        return [boxN, bestMove, myBestMoves[bestMove]]

    def boxRating(self, boxN, player, hypBoard, a, b):
        allMoves = [0] * 9
        options = hypBoard.guessSpotOrder(boxN)
        for spot in options:
            st = time()
            hypBoard.setSpot(boxN, spot, player)
            bestPath = self.moveRating(spot, otherPlayer(player), hypBoard, 0, True, a, b)
            allMoves[spot] = bestPath[0]

            # board.prtBoard()
            # print(bestPath)
            # bo = Board()
            # bo.fromString(bestPath[1])
            # bo.prtBoard()
            # print()
            # print()
            hypBoard.setSpot(boxN, spot, 0)
            print(spot, time() - st)

            a = max(a, allMoves[spot])
            if a >= b:
                return allMoves
        print(self.c, self.nc)
        self.c = 0
        self.nc = 0
        return allMoves

    previouslyCrunched = {}
    bigDepth = 4
    c = 0
    nc = 0

    def moveRating(self, boxN, player, cpyBoard, depth, maxPlayer, a, b):
        # if maximizingPlayer then:
        #     value: = −∞
        #     for each child of node do:
        #         value: = max(value, alphabeta(child, depth − 1, α, β, FALSE))
        #         α: = max(α, value)
        #         if α ≥ β then:
        #             break
        #             (*β cut-off *)
        #     return value
        # else:
        #     value: = +∞
        #     for each child of node do:
        #         value: = min(value, alphabeta(child, depth − 1, α, β, TRUE))
        #         β: = min(β, value)
        #         if α ≥ β then:
        #             break
        #             (*α cut-off *)
        # return value
        hypBoard = Board()
        hypBoard.copyBoard(cpyBoard)
        if depth > self.maxDepth:
            prediction = hypBoard.naiveWinPredict((otherPlayer(player) if maxPlayer else player))
            return [prediction, hypBoard.toString(boxN, player)]
        if hypBoard.boxWinner(boxN) != 0:
            boxes = [box for box in range(9) if hypBoard.boxWinner(box) == 0]
        else:
            boxes = [boxN]
        value = [-1000000000] if maxPlayer else [1000000000]
        for boxN in boxes:
            # options = hypBoard.guessSpotOrder(boxN)
            options = hypBoard.getOptions(boxN)
            for spot in options:
                hypBoard.setSpot(boxN, spot, player)
                if maxPlayer:
                    temp = self.moveRating(spot, otherPlayer(player), hypBoard, depth + 1, False, a, b)
                    if temp[0] > value[0]:
                        value = temp
                    a = max(a, value[0])
                else:
                    temp = self.moveRating(spot, otherPlayer(player), hypBoard, depth + 1, True, a, b)

                    if temp[0] < value[0]:
                        value = temp
                    b = min(b, value[0])
                hypBoard.setSpot(boxN, spot, 0)
                if a >= b:
                    self.c = self.c + 1
                    return value
                self.nc = self.nc + 1

        return value


#
players = []
aiPlayer1 = aiPlayer()
aiPlayer2 = aiPlayer()
players = [aiPlayer1, aiPlayer2]


def playGame():
    global player, players
    boxN = 3
    while board.gameWinner() == 0:
        # [boxN, spot] = getPlayerInput(boxN)
        [boxN, spot, rating] = aiPlayer1.play(player, board, boxN)
        board.setSpot(boxN, spot, player)
        board.prtBoard(boxN)
        updatePlayer()
        boxN = spot

        [boxN, spot, rating] = aiPlayer2.play(player, board, boxN)
        board.setSpot(boxN, spot, player)
        board.prtBoard(boxN)
        updatePlayer()
        boxN = spot

    print("player " + str(board.gameWinner()) + " won!!!")


board.prtBoard()
# playGame()
