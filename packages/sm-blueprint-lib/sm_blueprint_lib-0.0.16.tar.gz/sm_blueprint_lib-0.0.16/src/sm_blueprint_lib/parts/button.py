from dataclasses import dataclass, field

from ..bases.parts.baseinteractablepart import BaseInteractablePart
from ..constants import SHAPEID


@dataclass
class Button(BaseInteractablePart):
    """Class that represents a Button part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Button)
