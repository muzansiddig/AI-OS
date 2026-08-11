from app.artifacts.manager import artifacts

class ExecutionContext:

    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def export(self):
        return {
            "context": self.data,
            "artifacts": artifacts.all()
        }

context = ExecutionContext()
