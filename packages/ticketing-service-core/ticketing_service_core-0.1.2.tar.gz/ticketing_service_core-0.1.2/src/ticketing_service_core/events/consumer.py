"""
consumer module
"""
from abc import ABC, abstractmethod

class Consumer(ABC):
    """
    The consumer class is an abstract class from which all event consumers must inherit
    """
    @abstractmethod
    def consume(self, channel, body):
        """
        Consumes a message from the queue and takes some action as a result
        """
