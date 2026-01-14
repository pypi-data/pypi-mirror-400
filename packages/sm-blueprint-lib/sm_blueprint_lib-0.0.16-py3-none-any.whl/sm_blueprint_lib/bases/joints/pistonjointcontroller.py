from dataclasses import dataclass, field

from .basejointcontroller import BaseJointController


@dataclass
class PistonJointController(BaseJointController):
    length: int
    speed: int
