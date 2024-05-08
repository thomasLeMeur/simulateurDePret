from typing import TypeVar, Generic
from typing import Any, Protocol

from pydantic import BaseModel

from src.models import MaxCapacityModel

ConfigT = TypeVar("ConfigT", bound=BaseModel)
NbAnneesT = TypeVar("NbAnneesT", bound=MaxCapacityModel)


class SimulatorWithResultProtocol(Protocol):
    def succeed(self) -> bool: ...

    def has_better(self) -> bool: ...


class SuccesSimulator(SimulatorWithResultProtocol):
    def succeed(self):
        return True

    def has_better(self):
        return False


class AnneesSuccesSimulator(SimulatorWithResultProtocol, Generic[NbAnneesT]):
    nb_annees: int
    config: NbAnneesT

    def succeed(self):
        return self.nb_annees <= self.config.nb_annees

    def has_better(self):
        return self.nb_annees < self.config.nb_annees


class BaseSimulator(SimulatorWithResultProtocol, Generic[ConfigT]):
    config: ConfigT

    @staticmethod
    def get_model() -> type[ConfigT]: ...

    def __init__(self, config_as_dict: dict[str, Any]):
        self.config = self.get_model().model_validate(config_as_dict)

    def debrief(self): ...
