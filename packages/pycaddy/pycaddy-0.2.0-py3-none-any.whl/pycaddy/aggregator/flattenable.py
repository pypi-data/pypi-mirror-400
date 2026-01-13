from abc import ABC, abstractmethod


class Flattenable(ABC):
    @abstractmethod
    def flatten(self) -> dict:
        pass
