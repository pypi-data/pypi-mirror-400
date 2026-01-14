import random
import time


class Dummy:
    testme: int = 0

    def __init__(self):
        self.val = 3
        print("call me maybe")

    def read_temp(self, min: int, max: int) -> float:
        result = random.randint(min, max)
        print(f"returning result {result}")
        print(f"btw, foovar is {self.foovar}")
        return result

    def hello(self) -> str:
        self.testme += 1
        return "world"

    def _secret_hello(self) -> str:
        self.testme -= 1
        return "(secret) world"

    def blocking_call(self, block_time: int):
        print(f"I will start sleeping for {block_time} s now...")
        time.sleep(block_time)
        print("Done sleeping!")


class DependentDummy:
    def __init__(self, parent_hero):
        self.parent = parent_hero

    def update_parent_testme(self, value: int):
        self.parent.testme = value


class PolledDatasourceDummy(Dummy):
    foovar: str = ""
    testme: int = 0

    def _observable_data(self):
        print("new data got called")
        return self.testme
