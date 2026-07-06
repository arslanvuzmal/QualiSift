from abc import ABC, abstractmethod

class NotificationAdapter(ABC):
    @abstractmethod
    async def send(self, message: str, subject: str = None) -> bool:
        pass

class ConsoleAdapter(NotificationAdapter):
    async def send(self, message: str, subject: str = None) -> bool:
        print("\n--- NOTIFICATION START ---")
        if subject:
            print(f"Subject: {subject}")
        print(f"Message: {message}")
        print("--- NOTIFICATION END ---\n")
        return True
