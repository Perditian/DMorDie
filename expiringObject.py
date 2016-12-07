
import threading
import time

class ExpiringMessage(object):
    """docstring for ExpiringMessage"""

    def __init__(self, sender, content, duration):
        self.valid = True
        self.read = False
        self.sender = sender
        self.content = content
        self.mutex = threading.Lock()
        if duration > 0:
            self.thread = threading.Thread(target=self.delAfter, args=(duration,))
            self.thread.start()

    def readme(self):
        with self.mutex:
            self.read = True


    def delAfter(self, duration): #duration in seconds
        while duration > 0:
            time.sleep(1)
            duration -= 1
            with self.mutex:
                if self.read == True:
                    return

        with self.mutex:
            if self.read == False:
                self.valid = False
        
        return

    def clear(self):
        self.thread.join()