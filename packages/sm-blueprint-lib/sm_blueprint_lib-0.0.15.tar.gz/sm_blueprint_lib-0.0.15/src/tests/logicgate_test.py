from src.sm_blueprint_lib import *
import pprint as pp

bp = Blueprint()
print(get_current_id())
gate1 = LogicGate((1,2,3),PAINT_COLOR.Orange,MODE.AND,xaxis=3,zaxis=3)
pp.pprint(gate1)
print(get_current_id())
gate2 = LogicGate((4,3,2),PAINT_COLOR.Blue,"or")
pp.pprint(gate2)
print(get_current_id())
gate3 = LogicGate((1,1,1),PAINT_COLOR.Dark_Jungle_Green,2)
pp.pprint(gate3)
print(get_current_id())
timer = Timer((1,2,1),PAINT_COLOR.Yellow,(5,10))
pp.pprint(timer)
print(get_current_id())
button = Button((0,0,0),PAINT_COLOR.Red)
pp.pprint(button)
print(get_current_id())
gate1.connect(gate2)
gate2.connect(gate3)
gate3.connect(gate1)

bp.add(gate1,gate2,gate3,timer,button)

save_blueprint(bp,get_blueprint_path("sm_test_blueprint"))

print(get_current_id())

