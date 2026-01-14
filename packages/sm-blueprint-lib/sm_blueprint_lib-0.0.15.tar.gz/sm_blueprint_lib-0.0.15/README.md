# sm_blueprint_lib
 Scrap Mechanic Library for Blueprint manipulation.

## Instalation
```sh
pip install sm_blueprint_lib
```
## Updating version
```sh
pip install --upgrade sm_blueprint_lib
```
## Usage
```python
import numpy as np

import sm_blueprint_lib as sm

# Create a Blueprint object to store your parts
bp = sm.Blueprint()

# Define your stuff as you like, ID's are generated automatically or u can create them manually
# The controller argument is converted to the needed LogicGateController class

# There are 2 ways to set the mode of a controller
# 0: and, 1: or, 2: xor, 3: nand, 4: nor, 5: xnor
# "and", "or", "xor", "nand", "nor", "xnor"

# colors can be Defined as hex eg "1122ff" or as a RGB tuple eg (17, 34, 255)
# there is also the paint gun colors
# sm.PAINT_COLOR.Yellow
# You can even use the closet matching name
# sm.PAINT_COLOR.Barberry


single_and = sm.LogicGate(pos=(0, 0, 0), color="1122ff", controller=0)
single_or = sm.LogicGate(sm.Pos(0, 2, 0), sm.PAINT_COLOR.Blue, 1)
single_self_wired_xor = sm.LogicGate(
    pos=sm.Pos(0, 4, 0),
    color="5522ff",
    # Or define it explicitly
    controller=sm.LogicGateController(mode=2, id=9999999, controllers=[sm.ID(9999999)])
)

# Create multiple gates at the same time
row_0 = [sm.LogicGate((x, 6, 0), "ffffff", "and") for x in range(10)]
row_1 = [sm.LogicGate((-1, 6, z + 1), "ffffff", 0) for z in range(10)]
# Define matrices using numpy
matrix = np.ndarray((10, 10), dtype=sm.LogicGate)
for x in range(10):
    for z in range(10):
        # Define custom rotation (xaxis, zaxis)
        matrix[x, z] = sm.LogicGate(
            (x, 8, z + 1), "000000", 5, xaxis=1, zaxis=2)

single_nor = sm.LogicGate(sm.Pos(0, 11, 0), "ee22ff", 4)

row_2 = [sm.LogicGate((x, 13, 0), "ffffff", 0) for x in range(10)]
row_3 = [sm.LogicGate((-1, 13, z + 1), "ffffff", 0) for z in range(10)]

# Simple Timer loop
loop = [sm.LogicGate((4, 0, 0), "987654"),
        # TimerController can be passed as (seconds, ticks)
        sm.Timer((5, 0, 0), "3210ff", (1, 0)),
        sm.LogicGate((6, 0, 0), "eeddcc", 3)]

# Connect stuff
# 1 to 1
sm.connect(single_and, single_or)
sm.connect(single_or, single_self_wired_xor)
sm.connect(row_0, row_1)    # With parallel=True (ie row to row)
# 1 to many
sm.connect(single_self_wired_xor, row_0)
sm.connect(row_0, matrix)
# Many to 1
sm.connect(matrix, single_nor)
# Many to many
# With parallel=False (ie everything connects to everything)
sm.connect(row_2, row_3, parallel=False)
# You can also chain single gate connections
loop[0].connect(loop[1]).connect(loop[2]).connect(loop[0])

# Put all parts into the blueprint
# Note that it doesn't care if it's a single gate or arrays
bp.add(single_and, single_or, single_self_wired_xor,
       row_0, row_1, matrix, single_nor, row_2, row_3, loop)

# Finally, save the blueprint into a file or dump it as a string
print(sm.dump_string_from_blueprint(bp))

# To make a new blueprint
sm.make_new_blueprint("sm_lib_test_blueprint", bp)

# Or save over an existing blueprint
sm.save_blueprint("sm_lib_test_blueprint", bp)
```

### Results
#### 1 to 1 and loop
![1 to 1 and loop](1to1andloop.png)
#### Row to row and 1 to many
![row to row and 1 to many](rowtorowand1tomany.png)
#### Many to 1 and many to many
![many to 1 and many to many](manytooneandmanytomany.png)
