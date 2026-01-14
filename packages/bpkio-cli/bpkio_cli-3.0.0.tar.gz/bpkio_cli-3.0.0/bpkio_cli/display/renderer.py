from abc import ABC, abstractmethod

class ViewRenderer(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def render(self):
        pass
