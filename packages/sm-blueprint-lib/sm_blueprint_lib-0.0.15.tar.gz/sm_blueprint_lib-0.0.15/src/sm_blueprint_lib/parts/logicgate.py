from dataclasses import dataclass, field

from ..bases.parts.baselogicpart import BaseLogicPart
from ..bases.controllers.logicgatecontroller import LogicGateController
from ..constants import SHAPEID


@dataclass
class LogicGate(BaseLogicPart):
    """Class that represents a Logic Gate part.
    """
    controller: LogicGateController = field(
        default_factory=LogicGateController)
    shapeId: str = field(kw_only=True, default=SHAPEID.Logic_Gate)

    def __post_init__(self):
        super().__post_init__()
        # Can specify mode as a dict, a tuple (mode,) or just the parameter mode
        if not isinstance(self.controller, LogicGateController):
            try:
                self.controller = LogicGateController(**self.controller)
            except TypeError:
                try:
                    self.controller = LogicGateController(*self.controller)
                except TypeError:
                    self.controller = LogicGateController(self.controller)
