from unicurses import *
from unicguard import *
import sys


BLUE = None
RED = None
WHITE = None
GREEN = None
SHIP = None
HIT = None


LOG_WIN = None
def log(string):
  global LOG_WIN
  waddstr(LOG_WIN, str(string) + "\n")


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
    self.hits = []
    self.win = win
    self.target = None
    
  def draw(self):
    global BLUE, RED, WHITE, GREEN, SHIP, HIT
    for y in range(11):
      for x in range(11):
        c = "~"
        a = BLUE
        if (x-1,y-1) in self.hits:
          c = "O"
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


def main(args):
  global BLUE, RED, WHITE, GREEN, SHIP, HIT, LOG_WIN
  with unicurses_guard() as stdscr:
    #Color Styles
    BLUE = new_style(COLOR_CYAN, COLOR_BLACK)
    RED = new_style(COLOR_RED, COLOR_BLACK)
    WHITE = new_style(COLOR_WHITE, COLOR_BLACK)
    GREEN = new_style(COLOR_BLACK, COLOR_GREEN)
    SHIP = new_style(COLOR_BLACK, COLOR_YELLOW)
    HIT = new_style(COLOR_RED, COLOR_YELLOW)
    
    #LogWin
    LOG_WIN = newwin(20,49,14,0)
    logpan = new_panel(LOG_WIN)
    
    #Ocean wins
    ocWin1 = newwin(13, 24, 0, 0)
    ocPan1 = new_panel(ocWin1)
    oc1 = Ocean(ocWin1)
    ocWin2 = newwin(13, 24, 0, 25)
    ocPan2 = new_panel(ocWin2)
    oc2 = Ocean(ocWin2)

    #dev stuff
    oc1.ships.append(Ship((1,1), (1,0), 4, 4))
    oc2.target = [0,0]
    
    #drawing
    while 1:
      oc1.draw()
      oc2.draw()
      update_panels()
      doupdate()
      k = getkey()
      if k == "q":
        break
      elif k == "w" or k == "KEY_UP":
        oc2.target[1] -= 1
        if oc2.target[1] < 0:
          oc2.target[1] = 0
      elif k == "s" or k == "KEY_DOWN":
        oc2.target[1] += 1
        if oc2.target[1] >= 10:
          oc2.target[1] = 9
      elif k == "a" or k == "KEY_LEFT":
        oc2.target[0] -= 1
        if oc2.target[0] < 0:
          oc2.target[0] = 0
      elif k == "d" or k == "KEY_RIGHT":
        oc2.target[0] += 1
        if oc2.target[0] >= 10:
          oc2.target[0] = 9
      elif k == "\n":
        oc1.hits.append(tuple(oc2.target))
      log(oc1.hits)
    

if __name__=="__main__":
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
