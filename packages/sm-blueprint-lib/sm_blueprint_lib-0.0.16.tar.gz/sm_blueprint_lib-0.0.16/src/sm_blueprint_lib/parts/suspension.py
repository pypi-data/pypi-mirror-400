from dataclasses import dataclass, field

from ..bases.joints.suspensionjoint import SuspensionJoin
from ..constants import SHAPEID


@dataclass
class SportSuspension1(SuspensionJoin):
    """Class that represents a Sport Suspension 1 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sport_Suspension_1)


@dataclass
class SportSuspension2(SuspensionJoin):
    """Class that represents a Sport Suspension 2 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sport_Suspension_2)


@dataclass
class SportSuspension3(SuspensionJoin):
    """Class that represents a Sport Suspension 3 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sport_Suspension_3)


@dataclass
class SportSuspension4(SuspensionJoin):
    """Class that represents a Sport Suspension 4 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sport_Suspension_4)


@dataclass
class SportSuspension5(SuspensionJoin):
    """Class that represents a Sport Suspension 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Sport_Suspension_5)


@dataclass
class OffRoadSuspension1(SuspensionJoin):
    """Class that represents a Off-Road Suspension 1 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Off_Road_Suspension_1)


@dataclass
class OffRoadSuspension2(SuspensionJoin):
    """Class that represents a Off-Road Suspension 2 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Off_Road_Suspension_2)


@dataclass
class OffRoadSuspension3(SuspensionJoin):
    """Class that represents a Off-Road Suspension 3 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Off_Road_Suspension_3)


@dataclass
class OffRoadSuspension4(SuspensionJoin):
    """Class that represents a Off-Road Suspension 4 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Off_Road_Suspension_4)


@dataclass
class OffRoadSuspension5(SuspensionJoin):
    """Class that represents an Off-Road Suspension 5 part.
    """
    shapeId: str = field(kw_only=True, default=SHAPEID.Off_Road_Suspension_5)
