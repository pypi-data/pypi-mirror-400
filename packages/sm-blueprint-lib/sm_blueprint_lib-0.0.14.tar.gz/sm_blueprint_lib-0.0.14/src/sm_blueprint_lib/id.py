from dataclasses import dataclass

@dataclass
class ID:
    """Class that represents an ID object that the game uses to uniquely 
    identify Interactables, Joints, etc.
    """
    id: int