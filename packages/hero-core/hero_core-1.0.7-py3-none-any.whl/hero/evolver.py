
from ast import List
from dataclasses import dataclass

from hero_base import State


@dataclass
class EvolveResult:
    new_question: str
    additional_outputs: List[str]

def evolve(state: State) -> EvolveResult:
    pass