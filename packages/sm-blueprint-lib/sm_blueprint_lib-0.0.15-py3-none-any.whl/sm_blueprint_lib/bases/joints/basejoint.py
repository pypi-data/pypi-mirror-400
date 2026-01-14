from dataclasses import dataclass, field

from ...constants import SHAPEID
from ...pos import *


@dataclass
class BaseJoint:
    childA: int
    childB: int
    color: str
    id: int
    posA: Pos
    posB: Pos
    shapeId: str
    xaxisA: int
    xaxisB: int
    zaxisA: int
    zaxisB: int

    def __post_init__(self):
        self.posA = check_pos(self.posA)
        self.posB = check_pos(self.posB)

    def __init_subclass__(cls):
        super().__init_subclass__()
        try:
            SHAPEID.JOINT_TO_CLASS[cls.shapeId.default] = cls
        except AttributeError:
            pass
