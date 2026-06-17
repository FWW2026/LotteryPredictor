from abc import ABC
from abc import abstractmethod


class BasePredictor(ABC):

    name = "Base"

    @abstractmethod
    def predict(self, data):
        pass