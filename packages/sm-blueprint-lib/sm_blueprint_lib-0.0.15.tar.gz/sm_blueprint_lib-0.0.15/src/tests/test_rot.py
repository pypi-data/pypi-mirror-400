from pprint import pp

from src.sm_blueprint_lib import *

bp = Blueprint()

g0 = LogicGate((1, 0, 0), "ffffff")  # .rotate("up", "right")
g1 = LogicGate((2, 0, 0), "ffffff").rotate("up", "left")
g2 = LogicGate((3, 0, 0), "ffffff").rotate("up", "up")
g3 = LogicGate((4, 0, 0), "ffffff").rotate("up", "down")
g4 = LogicGate((5, 0, 0), "ffffff").rotate("up", "right")

bp.add(g0,
       g1,
       g2,
       g3,
       g4,
       # show the axis just for debugging
       Block((0, 0, -1), "ffffff", (1, 1, 1)),
       Block((1, -1, -1), "ff0000", (5, 3, 1)),
       Block((0, 1, -1), "00ff00", (1, 3, 1)),
       Block((0, 0, 0), "0000ff", (1, 1, 5)),
       )
path = utils.get_paths()[0]
pp(bp)

make_new_blueprint(path,"bob",bp)
