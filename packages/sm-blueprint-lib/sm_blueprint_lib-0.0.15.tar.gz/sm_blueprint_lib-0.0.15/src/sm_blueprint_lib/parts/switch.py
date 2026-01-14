from dataclasses import dataclass, field

from ..bases.parts.baselogicpart import BaseLogicPart
from ..constants import SHAPEID


@dataclass
class Switch(BaseLogicPart):
    """Class that represents a Switch part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Switch)
