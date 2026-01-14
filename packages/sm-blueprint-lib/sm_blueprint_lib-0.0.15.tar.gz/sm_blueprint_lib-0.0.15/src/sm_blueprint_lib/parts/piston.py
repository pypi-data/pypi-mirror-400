from dataclasses import dataclass, field

from ..bases.joints.pistonjoint import PistonJoint
from ..constants import SHAPEID


@dataclass
class Piston1(PistonJoint):
    """Class that represents a Piston 1 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Piston_1)


@dataclass
class Piston2(PistonJoint):
    """Class that represents a Piston 2 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Piston_2)


@dataclass
class Piston3(PistonJoint):
    """Class that represents a Piston 3 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Piston_3)


@dataclass
class Piston4(PistonJoint):
    """Class that represents a Piston 4 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Piston_4)


@dataclass
class Piston5(PistonJoint):
    """Class that represents a Piston 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Piston_5)
