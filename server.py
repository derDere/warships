from unicurses import *
from main import *
import datetime as dt
import random as rnd


LEFT = ["a","KEY_LEFT"]
RIGHT = ["d","KEY_RIGHT"]
UP = ["w","KEY_UP"]
DOWN = ["s","KEY_DOWN"]
ROTATE = ["r"," "]
ENTER = ["e","\n"]
QUIT = ["q"]


class AiConnector:
  def __init__(self):
    self.hits = []

  def checkOpponent(self):
    v = rnd.randrange(1000)
    if v % 3 == 0:
      return (4,4)
    return None
  
  def sendTarget(self, target):
    x,y = target
    if x % 2 == 0:
      return "X"
    else:
      return "O"


class Server:
  pass


class Client:
  pass


shipTurns = {
  (1,0): (0,1),
  (0,1): (-1,0),
  (-1,0): (0,-1),
  (0,-1): (1,0)
}


shipTypes = {
  1: 2,
  2: 3,
  3: 3,
  4: 4,
  5: 5
}


maxHits = sum(shipTypes.values())


def hitsLeft(oc):
  hitCount = len([x for x in oc.hits if oc.hits[x] == "X"])
  if hitCount < maxHits:
    return True
  else:
    return False


def addT(T1,T2):
  return tuple(sum(x) for x in zip(T1, T2))


class Game:
  def __init__(self, connector, draw):
    self.con = connector
    self.draw = draw
    self.logs = []
    self.logLength = 5
    self.Quit = False
    self.lastTarget = [4,4]
  
  def place(self, oc):
    global UP, LEFT, RIGHT, DOWN, ROTATE, QUIT, ENTER
    self.log("Place your warships...")
    for shipI in shipTypes:
      currentShip = Ship((0,0),(1,0),shipTypes[shipI],shipI)
      oc.ships.append(currentShip)
      self.log("Place warship #%d" % currentShip.index)
      shipPlaced = False
      while not shipPlaced:
        self.draw()
        key = getkey()
        x,y = currentShip.pos
        if key in UP:
          y -= 1
        elif key in DOWN:
          y += 1
        elif key in LEFT:
          x -= 1
        elif key in RIGHT:
          x += 1
        elif key in ROTATE:
          currentShip.dir = shipTurns[currentShip.dir]
        elif key in QUIT:
          exit()
        elif key in ENTER:
          isPlaceable = True
          for p in currentShip.points:
            if p[0] < 0 or p[0] >= 10 or p[1] < 0 or p[1] >= 10:
              isPlaceable = False
            else:
              for s in oc.ships:
                if s != currentShip:
                  for sp in s.points:
                    if sp == p:
                      isPlaceable = False
          if isPlaceable:
            shipPlaced = True
          else:
            self.log("Ship position invalid!")
        if x < 0: x = 0
        if x > 9: x = 9
        if y < 0: y = 0
        if y > 9: y = 9
        currentShip.pos = (x,y)
        currentShip.calc()
  
  def turn(self, oc):
    global UP, LEFT, RIGHT, DOWN, ROTATE, QUIT, ENTER
    self.log("choose your target...")
    oc.target = self.lastTarget
    choosen = False
    while not choosen:
      self.draw()
      key = getkey()
      if key in QUIT:
        exit()
      elif key in UP:
        oc.target[1] -= 1
        if oc.target[1] < 0:
          oc.target[1] = 0
      elif key in DOWN:
        oc.target[1] += 1
        if oc.target[1] >= 10:
          oc.target[1] = 9
      elif key in LEFT:
        oc.target[0] -= 1
        if oc.target[0] < 0:
          oc.target[0] = 0
      elif key in RIGHT:
        oc.target[0] += 1
        if oc.target[0] >= 10:
          oc.target[0] = 9
      elif key in ENTER:
        choosen = True
    self.lastTarget = oc.target
    target = tuple(oc.target)
    oc.target = None
    hit = self.con.sendTarget(target)
    oc.hits[target] = hit
    if hit == "O":
      self.log("You missed")
    else:
      self.log("You hit!")
  
  def wait(self, oc):
    self.log("Waiting for opponent...")
    hit = None
    while hit == None:
      self.draw()
      hit = self.con.checkOpponent()
      if hit == None:
        t.sleep(0.5)
    hitType = "O"
    for s in oc.ships:
      if hit in s.points:
        hitType = "X"
        self.log("Opponent hit!")
        break
    if hitType == "O":
      self.log("Opponent missed")
    oc.hits[hit] = hitType
  
  def log(self, msg):
    now = dt.datetime.now()
    self.logs.insert(0, "%02d:%02d:%02d -> %s" % (now.hour,now.minute,now.second,str(msg)))
    if len(self.logs) > self.logLength:
      self.logs = self.logs[:self.logLength]
