
import threading
import time

class ExpiringMessage(object):
    """docstring for ExpiringMessage"""



    def __init__(self, sender, content, duration):
        self.valid = True
        self.sender = sender
        self.content = content
        if duration != 0:
            self.thread = threading.Thread(target=self.delAfter, args=(duration,))
            self.thread.start()

    def delAfter(self, duration):
        time.sleep(duration)
        self.valid = False

    def clear(self):
        self.thread.join()