# main.py

class PythonAgent:
    def __init__(self, name):
        self.name = name

    def start(self):
        print(f"Agent {self.name} is starting...")

if __name__ == "__main__":
    agent = PythonAgent("DefaultAgent")
    agent.start()