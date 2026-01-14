import json
from pprint import pp
from src.sm_blueprint_lib import *

path = get_paths()[0]

blueprint = find_blueprint(path,"sm_test_blueprint")

blueprintPath = path+"/"+blueprint+"/blueprint.json"


with open(blueprintPath) as fp:
    bp = json.load(fp)
    all_parts = bp["bodies"][0]["childs"]
    all_fields = set()
    print(len(all_parts))

    for part in all_parts:
        all_fields |= set(part.keys())
    print(f"{all_fields=}")

    common_fields = all_fields.copy()
    for part in all_parts:
        common_fields &= set(part.keys())
    print(f"{common_fields=}")

    fields_boundable = all_fields.copy()
    for part in all_parts:
        if part.get("bounds"):
            fields_boundable &= set(part.keys())
    print(f"{fields_boundable=}")

    parts_with_controller = [p for p in all_parts if p.get("controller")]
    all_fields_controller = set([(SHAPEID.SHAPEID_TO_CLASS.get(
        p["shapeId"]), *tuple(p["controller"].keys())) for p in parts_with_controller])
    common_controller = list(set(x) for x in all_fields_controller.copy())
    print("common_controller=", end="")
    pp(common_controller, width=100)

    a = list(set(x) for x in all_fields_controller.copy())
    all_controller = set()
    for s in a:
        all_controller |= s
    pp(all_controller, width=100)

    common_controller = all_controller.copy()
    for s in a:
        common_controller &= s
    pp(common_controller, width=100)


j = ('{"bodies":[{"childs":[{"bounds":{"x":2,"y":2,"z":1},"color":"CE9E0C","pos":{"x":-13,"y":-7,"z":2},"shapeId":"09ca2713-28ee-4119-9622-e85490034758","xaxis":1,"zaxis":3},'
     '{"color":"DF7F01","controller":{"active":false,"controllers":[{"id":7227441}],"id":7227439,"joints":null,"seconds":2,"ticks":1},"pos":{"x":-12,"y":-5,"z":3},"shapeId":"8f7fd0e7-c46e-4944-a414-7ce2437bb30f","xaxis":1,"zaxis":-2},'
     '{"color":"DF7F01","controller":{"active":true,"controllers":[{"id":7227439}],"id":7227440,"joints":null,"mode":3},"pos":{"x":-12,"y":-6,"z":3},"shapeId":"9f0f56e8-2c31-4d83-996c-d00a9b296c3f","xaxis":1,"zaxis":-2},'
     '{"color":"DF7F01","controller":{"active":false,"controllers":[{"id":7227440}],"id":7227441,"joints":null,"mode":0},"pos":{"x":-13,"y":-6,"z":3},"shapeId":"9f0f56e8-2c31-4d83-996c-d00a9b296c3f","xaxis":1,"zaxis":-2}]}],"version":4}')

bp = load_blueprint_from_string(j)
pp(bp)
pp(Sensor5((1,2,3),(255,255,255),(False, False, (255,255,255), True, 5)))

print(BaseController())
a = BaseInteractablePart("a", (1, 2, 3), (255, 0, 0), xaxis=1, zaxis=3)
b = BaseInteractablePart("b", (2, 3, 4), (255, 0, 0), xaxis=1, zaxis=3)
a.connect(b)
print(a)
print(b)
print(BaseLogicController())
print(BaseLogicPart("c", (3, 4, 5), (20, 30, 10)))
print(LogicGateController())
l0 = LogicGate((0, 0, 0), (1, 2, 3))
l1 = LogicGate((0, 0, 0), (1, 2, 3))
l0.connect(l1)
pp(l0)
pp(l1)
path = blueprintPath
bp = load_blueprint(path)
pp(bp)


p = bases.parts.baseboundablepart.BaseBoundablePart("a",
                                                 (0, 2, 3),
                                                 (0, 0, 0),
                                                 (1, 1, 1))
pp(json.dumps(asdict(p)))

j = '{"shapeId": "aa", "pos": {"x": 0, "y": 2, "z": 3}, "color": "000000", "xaxis": 0, "zaxis": 1}'
p2 = bases.parts.basepart.BasePart(**json.loads(j))
pp(p2)

j = '{"shapeId": "a", "pos": {"x": 0, "y": 2, "z": 3}, "color": "000000", "bounds": {"x": 1, "y": 1, "z": 1} }'
p2 = bases.parts.baseboundablepart.BaseBoundablePart(**json.loads(j))
pp(p2)


j = '''{
                    "bounds": { "x": 1, "y": 1, "z": 1 },
                    "color": "CE9E0C",
                    "pos": { "x": 4, "y": 23, "z": 12 },
                    "shapeId": "09ca2713-28ee-4119-9622-e85490034758",
                    "xaxis": 1,
                    "zaxis": 3
}'''
p2 = blocks.barrierblock.BarrierBlock(**json.loads(j))
pp(p2)

bp = load_blueprint(path)
pp(bp)
pp(json.dumps(asdict(bp)))
save_blueprint(bp, path)

pp(constants.SHAPEID.SHAPEID_TO_CLASS)

pp(Blueprint())


print("test passed")