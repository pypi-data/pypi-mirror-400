from typing import Dict, Any, List


class SimpleMemory:
    """Simple memory for storing context or other information that shouldn't
    ever change between prompts.
    """

    def __init__(self):
        self.memories: Dict[str, Any] = dict()

    def load_variable(self, variable: str) -> Any:
        return self.memories[variable]

    def set_variable(self, variable: str, value: Any):
        self.memories[variable] = value

    def has_variable(self, variable: str):
        return variable in self.memories

    def append_history(self, message: str):
        if self.has_variable("history"):
            history: List[str] = self.load_variable("history")
        else:
            history = []
        if message:
            history.append(message)
        self.set_variable("history", history)

    def load_history(self):
        if self.has_variable("history"):
            history: List[str] = self.load_variable("history")
        else:
            history = []
        return history

    def clear(self) -> None:
        """Nothing to clear, got a memory like a vault."""
        self.memories.clear()


if __name__ == '__main__':
    memory = SimpleMemory()
    memory.set_variable('test', 'test')
    v = memory.load_variable('test')
    print(v)
