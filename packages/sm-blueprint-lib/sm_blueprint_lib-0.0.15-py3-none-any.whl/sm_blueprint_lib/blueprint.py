from dataclasses import dataclass, field
from typing import Optional

from .bases.parts.basepart import BasePart
from .body import Body
from .bases.joints.basejoint import BaseJoint
from .constants import VERSION, SHAPEID


@dataclass
class Blueprint:
    """Class that represents a Blueprint structure.
    It is type hinted, meaning you can access its members
    with the dot syntax instead of direcly indexing a JSON object.
    """
    bodies: list[Body] = field(default_factory=lambda: [{}])
    joints: Optional[list[BaseJoint]] = None
    version: int = VERSION.BLUEPRINT_VERSION

    def __post_init__(self):
        self.bodies = [Body(**body)
                       if not isinstance(body, Body) else
                       body
                       for body in self.bodies]
        if self.joints:
            self.joints = [SHAPEID.JOINT_TO_CLASS[j["shapeId"]](**j)
                           if not isinstance(j, BaseJoint) else
                           j
                           for j in self.joints]

    def add(self, *obj, body=0):
        """Adds the object(s) to the blueprint.

        Args:
            obj (Any): Can be a instance of BasePart or a subclass. It also can be any nested iterable of instances (list of parts, list of lists of parts, etc).
            body (int, optional): Specify in which blueprint's body the object will be placed. Defaults to 0.
        """
        for subobj in obj:
            if isinstance(subobj, BasePart):
                self.bodies[body].childs.append(subobj)
            else:
                for subsubobj in subobj:
                    self.add(subsubobj, body=body)
