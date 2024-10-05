from abc import ABC, abstractmethod


class ICommand(ABC):
    @abstractmethod
    async def execute(self, message: str) -> bool:
        pass
