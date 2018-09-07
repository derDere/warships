from unicurses import *
from unicguard import *
from server import *
import time as t
import sys


BLUE = None
RED = None
WHITE = None
GREEN = None
SHIP = None
HIT = None
LOG = None


class Ship:
  def __init__(self, pos, dir, length, index):
    self.index = index
    self.pos = pos
    self.dir = dir
    self.length = length
    self.points = []
    self.calc()
    
  def calc(self):
    point = self.pos
    self.points = [point]
    for i in range(self.length - 1):
      self.points.append(tuple(sum(x) for x in zip(self.points[-1], self.dir)))


class Ocean:
  def __init__(self, win):
    self.ships = []
    self.hits = {}
    self.win = win
    self.target = None
  
  def life(self):
    hitCount = len([x for x in self.hits if self.hits[x] == "X"])
    return maxHits - hitCount
    
  def draw(self):
    global BLUE, RED, WHITE, GREEN, SHIP, HIT
    for y in range(11):
      for x in range(11):
        c = "~"
        a = BLUE
        if (x-1,y-1) in self.hits:
          c = self.hits[(x-1,y-1)]
        if x == 0 and y == 0:
          c = " "
          a = WHITE
        elif x == 0:
          c = str(' ABCDEFGIHJ'[y])
          a = WHITE
        elif y == 0:
          c = str(x%10)
          a = WHITE
        else:
          for ship in self.ships:
            if (x-1,y-1) in ship.points:
              if (x-1,y-1) in self.hits:
                c = "X"
                a = HIT
              else:
                c = str(ship.index)
                a = SHIP
              c = c + " "
              break
        if self.target != None:
          Tx, Ty = self.target
          if x-1 == Tx or y-1 == Ty:
            a = GREEN
            if y-1 == Ty and len(c) < 2:
              c = c + " "
        a = color_pair(a)
        mvwaddstr(self.win, y + 1, x * 2 + 2, " ")
        wattron(self.win, a)
        mvwaddstr(self.win, y + 1, x * 2 + 1, c)
        wattroff(self.win, a)
    box(self.win)


myOc = None
opponentOc = None
game = None
logWin = None


def draw():
  global WHITE, LOG, logWin, game, myOc, opponentOc
  mvaddstr(14, 0, " " * 49)
  mvaddstr(14, 0, "         HP:%02d                    HP:%02d" % (myOc.life(), opponentOc.life()), WHITE)
  wbkgd(logWin, " ", color_pair(WHITE))
  wmove(logWin, 0, 0)
  for line in game.logs:
    waddstr(logWin, "%s\n" % line, color_pair(LOG))
  myOc.draw()
  opponentOc.draw()
  update_panels()
  doupdate()


def drawAndEnd(game, msg):
  game.log(msg)
  draw()
  while not getkey() in ["\n","q","e"]:
    pass
  exit()
  

def main(args):
  global BLUE, RED, WHITE, GREEN, SHIP, HIT, LOG, logWin, myOc, opponentOc, game
  con = AiConnector()
  game = Game(con, draw)
  
  with unicurses_guard() as stdscr:
    #Color Styles
    BLUE = new_style(COLOR_CYAN, COLOR_BLACK)
    RED = new_style(COLOR_RED, COLOR_BLACK)
    WHITE = new_style(COLOR_WHITE, COLOR_BLACK)
    GREEN = new_style(COLOR_BLACK, COLOR_GREEN)
    SHIP = new_style(COLOR_BLACK, COLOR_YELLOW)
    HIT = new_style(COLOR_RED, COLOR_YELLOW)
    LOG = new_style(COLOR_GREEN, COLOR_BLACK)
    
    mvaddstr(0,10,"YOU",color_pair(WHITE))
    mvaddstr(0,33,"Opponent",color_pair(RED))
    
    #LogWin
    logWin = newwin(20,49,15,0)
    logpan = new_panel(logWin)
    
    #Ocean wins
    ocWin1 = newwin(13, 24, 1, 0)
    ocPan1 = new_panel(ocWin1)
    myOc = Ocean(ocWin1)
    ocWin2 = newwin(13, 24, 1, 25)
    ocPan2 = new_panel(ocWin2)
    opponentOc = Ocean(ocWin2)
    
    game.place(myOc)
    while True:
      game.turn(opponentOc)
      if opponentOc.life() <= 0:
        drawAndEnd(game, "You won!")
      game.wait(myOc)
      if myOc.life() <= 0:
        drawAndEnd(game, "You lost!")
    

if __name__=="__main__":
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
