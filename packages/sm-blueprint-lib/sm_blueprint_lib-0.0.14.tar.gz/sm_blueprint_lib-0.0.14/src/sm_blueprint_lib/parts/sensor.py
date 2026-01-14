from dataclasses import dataclass, field

from ..bases.controllers.sensorcontroller import SensorController
from ..bases.parts.baseinteractablepart import BaseInteractablePart
from ..constants import SHAPEID


@dataclass
class BaseSensor(BaseInteractablePart):
    """Base class for Sensors.
    """
    controller: SensorController = field(
        default_factory=SensorController)

    def __post_init__(self):
        super().__post_init__()
        # Can specify sensor controller as a dict, a tuple (audioEnable, buttonMode, color, colorMode, range) or just the parameter mode
        if not isinstance(self.controller, SensorController):
            try:
                self.controller = SensorController(**self.controller)
            except TypeError:
                try:
                    self.controller = SensorController(*self.controller)
                except TypeError:
                    self.controller = SensorController(self.controller)


@dataclass
class Sensor1(BaseSensor):
    """Class that represents a Sensor 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sensor_1)


@dataclass
class Sensor2(BaseSensor):
    """Class that represents a Sensor 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sensor_2)


@dataclass
class Sensor3(BaseSensor):
    """Class that represents a Sensor 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sensor_3)


@dataclass
class Sensor4(BaseSensor):
    """Class that represents a Sensor 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sensor_4)


@dataclass
class Sensor5(BaseSensor):
    """Class that represents a Sensor 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sensor_5)
