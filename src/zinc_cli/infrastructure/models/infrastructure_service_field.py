import os
from typing import Union


class InfrastructureServiceField:
    def __init__(self, key: str, default_value: str = None):
        self.key: str = key
        self.value: str = default_value
        self.was_edited: bool = False

    def set(self, value: Union[str, bool]):
        if type(value) is bool:
            value = str(value)

        self.value = value
        self.was_edited = True
        if type(self.value) is not str:
            raise Exception(f"The value for {self.key} must be str, but is instead {type(self.value)}.")

    def write_to_environ(self):
        os.environ[self.key] = str(self.value)

    def load_from_environ(self):
        if self.key in os.environ:
            self.value = os.environ[self.key]
