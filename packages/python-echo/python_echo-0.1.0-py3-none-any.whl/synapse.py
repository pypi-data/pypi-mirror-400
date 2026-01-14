from abc import ABC, abstractmethod


class Synapse(ABC):
    @abstractmethod
    def prompt(self, text: str) -> str:
        raise NotImplementedError
