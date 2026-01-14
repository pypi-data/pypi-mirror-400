from dataclasses import dataclass, field

from .basecontroller import BaseController


@dataclass
class SensorController(BaseController):
    """Sensor's Controller
    """
    audioEnabled: bool
    buttonMode: bool
    color: str
    colorMode: bool
    range: int

    def __post_init__(self):
        super().__post_init__()
        # if color given as (r, g, b) then convert to hex string
        if not isinstance(self.color, str):
            self.color = "%02X%02X%02X" % (
                self.color[0], self.color[1], self.color[2])
        self.audioEnabled = bool(self.audioEnabled)
        self.buttonMode = bool(self.buttonMode)
        self.colorMode = bool(self.colorMode)
