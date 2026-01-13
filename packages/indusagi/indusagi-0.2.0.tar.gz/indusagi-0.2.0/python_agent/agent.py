class PythonAgent:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, I am {self.name}, your Python agent."

if __name__ == "__main__":
    agent = PythonAgent("Agent007")
    print(agent.greet())