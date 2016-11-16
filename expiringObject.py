
import threading

class ExpiringMessage(object):
    """docstring for ExpiringMessage"""
    def __init__(self, sender, content, duration):
        self.valid = true
        self.sender = sender
        self.content = content
        if duration != 0:
            self.thread = threading.thread(target=delAfter, args={duration})
            self.thread.start()

    def delAfter(duration):
        sleep(duration)
        self.valid = false

    def clear(self)
        self.thread.join()