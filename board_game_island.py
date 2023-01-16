from random import randint, choice, shuffle
from collections import Counter

def nop(p, g):
    return
class Space:
    def __init__(self, in_volcano = False):
        self.prev = None
        self.next = None
        self.action = nop #what happens when you land on the space
        self.nextaction = nop #what happens trying to move off the space
        self.in_volcano = in_volcano

board = [Space() for i in range(74)]
for i in range(73):
    board[i].next = board[i+1]
    board[i+1].prev = board[i]
board[0].prev = board[0] #relevant for tornado
board[-1].next = board[-1] #relevant for final movement roll

#every special space gets a function
def plus(n, p, g):
    for _ in range(n):
        p.space = p.space.next
def plusn(n):
    out = lambda p, g: plus(n, p, g)
    out.__name__ = '+'+str(n)
    return out
def minus(n, p, g):
    for _ in range(n):
        p.space = p.space.prev
def minusn(n):
    out = lambda p, g: minus(n, p, g)
    out.__name__ = '-'+str(n)
    return out
def dino(n):
    return lambda p, g: plus(10, p, g) if randint(0, 1) else minus(n, p, g)
def erupt(p, g):
    g.eruption = 3
def getPlayers(p, g, ufo_space = None): #not an action
    out = []
    for player in g.players:
        if player != p and \
        not player.space.in_volcano and \
        player.space != ufo_space:
            out.append(player)
    return out
def ufo(p, g):
    ps = getPlayers(p, g, p.space)
    if ps:
        op = choice(ps)
        p.space, op.space = op.space, p.space
def tornado(p, g):
    ps = getPlayers(p, g)
    if ps:
        minus(randint(4, 6), choice(ps), g)
def _1v1(p, g):
    ps = getPlayers(p, g)
    if ps:
        opponent = choice(ps) #TODO
        won = randint(0, 1)
        if won:
            plus(7, p, g)
            minus(7, opponent, g)
def _1v3(p, g):
    won = randint(0, 1)
    if won:
        plus(10, p, g)

#nextactions
def vine(p, g):
    plus(randint(1, 6), p, g)
def wall(p, g):
    if g.wall_passed or randint(0, 1):
        g.wall_passed = True
    else:
        p.moves = 0
riverspace = Space()
riverspace.prev = board[39]
riverspace.next = board[40]
def river(p, g):
    if randint(0, 1):
        p.moves = 0
        p.space = riverspace
spikeballspace = Space()
spikeballspace.prev = board[45]
spikeballspace.next = board[46]
def pit(p, g):
    if randint(1, 6) < 3:
        p.moves = 0
        p.space = v2[0] #spikeballspace.action(p, g)
def spikeball(p, g):
    if randint(1, 6) >= g.spikeball_number:
        g.spikeball_number = 0
    else:
        p.moves = 0
        for i in range(46, 57):
            for j in g.players:
                if j.space == board[i]:
                    j.space = spikeballspace
        if g.spikeball_number > 2:
            g.spikeball_number -= 1

#and here they are on the board
actions = {1:plusn(6), 9:plusn(6), \
11:plusn(4), 12:_1v3, 15:ufo, 16:plusn(4), \
20:tornado, 21:minusn(4), 25:_1v3, \
26:plusn(18), 27:..., 28:plusn(16), \
31:dino(9), 32:plusn(5), 33:erupt, \
34:tornado, 36:plusn(6), 37:_1v1, \
38:ufo, 41:plusn(6), 42:minusn(18), \
43:dino(4), 45:_1v3, 47:plusn(6), \
48:_1v1, 50:plusn(5), 52:plusn(4), \
53:ufo, 57:plusn(6), 58:_1v1, 61:plusn(5), \
63:tornado, 64:minusn(4), 66:..., \
67:tornado, 71:ufo, 72:minusn(4)}
for n in actions:
    board[n].action = actions[n]
board[6].nextaction = vine
board[22].nextaction = wall
board[39].nextaction = river
board[45].nextaction = pit
board[56].nextaction = spikeball

def warp(s, p, g):
    p.space = s
def volcano(volcano_space):
    out = [Space(in_volcano = True) for i in range(9)]
    for i in range(8):
        out[i].next = out[i+1]
        out[i+1].prev = out[i]
    out[0].prev = volcano_space #relevant for dist to end
    out[8].next = volcano_space.next
    
    out[1].action = plusn(4)
    out[3].action = plusn(4)
    out[4].action = lambda p, g: warp(volcano_space, p, g)
    
    volcano_space.action = lambda p, g: warp(out[0], p, g)
    return out
v1 = volcano(board[27])
v2 = volcano(spikeballspace)
v3 = volcano(board[66])

class Player:
    def __init__(self):
        self.space = board[0]
        self.moves = None
class GlobalState:
    def __init__(self):
        self.eruption = 0 #can be up to 3 turns
        self.wall_passed = False
        self.spikeball_number = 5
        self.rounds = 0
        self.winner = None
        self.players = [Player() for i in range(4)]

def roll(place):
    if place == 4:
        return randint(1, 6)
    sides = [None, 6, 3, 2][place]
    r1, r2 = randint(1, 6), randint(1, sides)
    if r1 == r2:
        r3 = randint(1, 6)
        return r1 + r2 + r3
    return r1 + r2
    
def doRound(g):
    g.rounds += 1
    shuffle(g.players) #oops! all lucky launch
    for turn in range(4):
        p = g.players[turn]
        p.moves = roll(turn+1)
        #print('roll', p.moves)
        if p.space == board[-1]:
            if p.moves >= 6:
                g.winner = p
                break
        while p.moves:
            p.space.nextaction(p, g)
            if p.moves:
                p.moves -= 1
                p.space = p.space.next
        if p.space == board[-1]:
            if randint(1, 6) == 6:
                g.winner = p
                break
        elif p.space == spikeballspace:
            pass #don't fall in or -4 after the spikeball rolls down
        elif g.eruption >= 0:
            while p.space.action != nop:
                minus(4, p, g)
        else:
            p.space.action(p, g)
        if g.eruption >= 0:
            g.eruption -= 1

nop.__name__ = '.'
def printSpace(s, g):
    out = ''
    out += '[' + s.action.__name__
    for p in g.players:
        if p.space == s:
            out += ' P'
    out += ']'
    return out
def printBoard(b, g):
    for s in b:
        print(printSpace(s, g), end = '')
    print()
def pbs(g):
    for b in [board, [riverspace, spikeballspace], v1, v2, v3]:
        printBoard(b, g)

def game():
    g = GlobalState()
    while not g.winner:
        doRound(g)
        #pbs(g)
    return g.rounds, g.winner
print(game())
r = []
for _ in range(10000):
    r.append(game()[0])
r.sort()
print(Counter(r))
print(r[:20])
print(r[-20:])