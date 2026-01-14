from dataclasses import dataclass, field

from .baselogiccontroller import BaseLogicController


@dataclass
class LogicGateController(BaseLogicController):
    """Logic Gate's Controller
    """
    mode: int|str = "or"

    def __post_init__(self):
        if type(self.mode) == str:
            match self.mode:
                case "and":
                    self.mode = 0
                case "or":
                    self.mode = 1
                case "xor":
                    self.mode = 2
                case "nand":
                    self.mode = 3
                case "nor":
                    self.mode = 4
                case "xnor":
                    self.mode = 5
                case _:
                    self.mode = 0