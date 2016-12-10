"""
 Avita Sharma, Eric Wyss, Davis Taus
 Expiring Message class
 Creates Messages which expire after a given time.
"""
import threading
import time

class ExpiringMessage(object):
    # Needs the sender, content, and number of seconds before it expires
    def __init__(self, sender, content, duration):
        self.valid = True
        self.read = False
        self.sender = sender
        self.content = content
        self.mutex = threading.Lock()
        if duration > 0:
            self.thread = threading.Thread(target=self.delAfter, 
                                           args=(duration,))
            self.thread.start()

    # Message has been read:
    def readme(self):
        with self.mutex:
            self.read = True

    # Expire after duration in seconds:
    def delAfter(self, duration):
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

    # clean up all messages:
    def clear(self):
        self.thread.join()