from dataclasses import dataclass, field

from .basejointcontroller import BaseJointController


@dataclass
class SuspensionJointController(BaseJointController):
    stiffnessLevel: int
