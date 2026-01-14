from dataclasses import dataclass, field

from ..bases.controllers.timercontroller import TimerController
from ..bases.parts.baselogicpart import BaseLogicPart
from ..constants import SHAPEID


@dataclass
class Timer(BaseLogicPart):
    """Class that represents a Timer logic part.
    """
    controller: TimerController = field(default_factory=TimerController)
    shapeId: str = field(kw_only=True, default=SHAPEID.Timer)

    def __post_init__(self):
        super().__post_init__()
        # Can provide seconds and ticks as a the TimerController class itself, a dict or a tuple (seconds, tick)
        if not isinstance(self.controller, TimerController):
            try:
                self.controller = TimerController(**self.controller)
            except TypeError:
                self.controller = TimerController(*self.controller)