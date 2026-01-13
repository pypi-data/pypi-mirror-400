from hero_base import State


state = State("mock_workspace", [])

class Test:
    
    def __init__(self, value: str):
        self.value = value

state.set_storage("test", Test("mock data"))

test = state.get_storage("test")

assert test.value == "mock data"

assert state.get_storage("none") == None

assert isinstance(state.get_storage("dict", {}), dict) == True

print(state.get_working_tree())