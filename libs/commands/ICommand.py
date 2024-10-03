from abc import ABC, abstractmethod


class ICommand(ABC):
    @abstractmethod
    async def execute(self) -> bool:
        pass

    @abstractmethod
    def process_message(self) -> dict:
        pass
