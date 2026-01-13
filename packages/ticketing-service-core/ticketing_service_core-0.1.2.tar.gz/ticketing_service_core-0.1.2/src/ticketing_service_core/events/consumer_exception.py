"""
consumer_exception Module
"""

class ConsumerException(Exception):
    """
    A ConsumerException should be raised by any consumers if they encounter an error
    while processing a message received from the broker. This allows the EventHandler
    to decide whether to ACK or NACK the message and respond to RPC calls. 
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
