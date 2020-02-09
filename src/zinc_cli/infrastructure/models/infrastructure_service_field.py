import os
from typing import Union


class InfrastructureServiceField:
    def __init__(self, key: str, default_value: Union[str, bool] = None):
        self.key: str = key
        self.value: Union[str, bool] = default_value
        self.was_edited: bool = False

    def set(self, value: Union[str, bool]):
        self.value = value
        self.was_edited = True
        if type(self.value) is not str and type(self.value) is not bool:
            raise Exception(f"The value for {self.key} must be str or bool, but is instead {type(self.value)}.")

    def write_to_environ(self):
        os.environ[self.key] = str(self.value)

    def load_from_environ(self):
        if self.key in os.environ:

            # Load from the environment.
            self.value = os.environ[self.key]

            # Able to serialize to and from a bool.
            if self.value == str(True):
                self.value = True

            if self.value == str(False):
                self.value = False
