from dataclasses import dataclass

from .basejoint import BaseJoint
from .pistonjointcontroller import PistonJointController


@dataclass
class PistonJoint(BaseJoint):
    controller: PistonJointController

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.controller, PistonJointController):
            self.controller = PistonJointController(**self.controller)
