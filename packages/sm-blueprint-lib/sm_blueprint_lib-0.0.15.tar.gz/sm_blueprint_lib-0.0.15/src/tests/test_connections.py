from pprint import pp
from numpy import ndarray
from src.sm_blueprint_lib import *

size = 10
l0 = [
    LogicGate((x+1, 0, 0), "FF0000", x % 6)
    for x in range(size)
]

l1 = [
    LogicGate((0, x+1, 0), "00FF00", x % 6)
    for x in range(size)
]

l2 = [
    LogicGate((0, 0, x+1), "0000FF", x % 6)
    for x in range(size)
]

# l3 = [
#     [Timer((x+1, y+1, x+y), "000000", (2, 1)) for y in range(size)]
#     for x in range(size)
# ]
l3 = ndarray((size, size), dtype=Timer)
for x in range(size):
    for y in range(size):
        l3[x, y] = Timer((x+1, y+1, x+y), "000000", (2, 1))
base = BarrierBlock((0, -1, -1), "000000", (size+1, size+1, 1))
zero = BarrierBlock((0, -1, 0), "000000", (1, 1, 1))

s = Switch((10, 10, 0), "ff0000")
b = Button((9, 10, 0), "ff0000")
g = LogicGate((8, 10, 0), "ff0000")

bp = Blueprint()
# print(dump_string_from_blueprint(bp))

connect(s, l1)
connect(l0, l1)
connect(l0, l3)
connect(l3, l2[-1])
connect(l1, l2, parallel=False)
connect(l3.T, l1)

bp.add(l0, l1, l2, base, zero, l3, s, b, g)

# bp.add(l0)
# bp.add(l1)
# bp.add(l2)

# bp.add(base)
# bp.add(zero)
# bp.add(l3)


# bp.bodies[0].childs.extend(l0)
# bp.bodies[0].childs.extend(l1)
# bp.bodies[0].childs.extend(l2)

# bp.bodies[0].childs.append(base)
# bp.bodies[0].childs.append(zero)

# for l in l3:
#     bp.bodies[0].childs.extend(l)

pp(load_blueprint_from_string('{"bodies":[{"childs":[{"bounds":{"x":2,"y":2,"z":1},"color":"CE9E0C","joints":[{"id":4298},{"id":4283}],"pos":{"x":7,"y":-3,"z":8},"shapeId":"09ca2713-28ee-4119-9622-e85490034758","xaxis":1,"zaxis":3}]},{"childs":[{"bounds":{"x":2,"y":2,"z":1},"color":"CE9E0C","joints":[{"id":4282},{"id":4283}],"pos":{"x":7,"y":-3,"z":5},"shapeId":"09ca2713-28ee-4119-9622-e85490034758","xaxis":1,"zaxis":3}]},{"childs":[{"bounds":{"x":1,"y":1,"z":1},"color":"CE9E0C","joints":[{"id":4298}],"pos":{"x":3,"y":-2,"z":8},"shapeId":"09ca2713-28ee-4119-9622-e85490034758","xaxis":1,"zaxis":3}]},{"childs":[{"bounds":{"x":2,"y":2,"z":1},"color":"CE9E0C","joints":[{"id":4281},{"id":4282}],"pos":{"x":7,"y":-3,"z":3},"shapeId":"09ca2713-28ee-4119-9622-e85490034758","xaxis":1,"zaxis":3}]},{"childs":[{"bounds":{"x":2,"y":2,"z":1},"color":"CE9E0C","joints":[{"id":4281}],"pos":{"x":7,"y":-3,"z":2},"shapeId":"09ca2713-28ee-4119-9622-e85490034758","xaxis":1,"zaxis":3}]}],"joints":[{"childA":4,"childB":3,"color":"DF7F01","id":4281,"posA":{"x":7,"y":-2,"z":3},"posB":{"x":7,"y":-2,"z":3},"shapeId":"4a1b886b-913e-4aad-b5b6-6e41b0db23a6","xaxisA":1,"xaxisB":1,"zaxisA":3,"zaxisB":3},{"childA":3,"childB":1,"color":"DF7F01","controller":{"controllers":null,"id":9299772,"joints":null,"length":0,"speed":0},"id":4282,"posA":{"x":7,"y":-2,"z":4},"posB":{"x":7,"y":-2,"z":5},"shapeId":"2f004fdf-bfb0-46f3-a7ac-7711100bee0c","xaxisA":1,"xaxisB":1,"zaxisA":3,"zaxisB":3},{"childA":1,"childB":0,"color":"DF7F01","controller":{"controllers":null,"id":9299773,"joints":null,"stiffnessLevel":1},"id":4283,"posA":{"x":7,"y":-2,"z":6},"posB":{"x":7,"y":-2,"z":8},"shapeId":"52855106-a95c-4427-9970-3f227109b66d","xaxisA":1,"xaxisB":1,"zaxisA":3,"zaxisB":3},{"childA":0,"childB":2,"color":"DF7F01","controller":{"controllers":null,"id":9299786,"joints":null,"stiffnessLevel":1},"id":4298,"posA":{"x":6,"y":-2,"z":8},"posB":{"x":3,"y":-2,"z":8},"shapeId":"73f838db-783e-4a41-bc0f-9008967780f3","xaxisA":2,"xaxisB":2,"zaxisA":-1,"zaxisB":-1}],"version":4}'))

print(len(bp.bodies[0].childs))
path = get_paths()[0]
save_blueprint(bp, path)
