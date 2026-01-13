class MockSSM:
    def __init__(self):
        self.params = {}

    def put(self, name, value):
        self.params[name] = value

    def get(self, name):
        return self.params.get(name)


SSM = MockSSM()
