from dataclasses import dataclass, field
from typing import Any, Optional

from ...constants import get_new_id
from ...id import ID


@dataclass
class BaseController:
    """Base class for controller objects (used in interactable parts and so)
    """
    controllers: Optional[list[ID]] = field(kw_only=True, default=None)
    id: int = field(kw_only=True, default_factory=get_new_id)
    joints: Optional[list[ID]] = field(kw_only=True, default=None)

    def __post_init__(self):
        try:
            self.controllers = [ID(**c) for c in self.controllers]
        except TypeError:
            pass