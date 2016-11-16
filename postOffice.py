import expiringMessage
import threading

class PostOffice(object):
    """docstring for PostOffice"""

    def __init__(self):
        self.PO_Boxes = {}
        self.addresses = []
        self.mutex = threading.Lock()

    def add_name(self, PID):
        with self.mutex:
            self.PO_Boxes[PID] = []
            self.addresses.append(PID)
    

    def send_message(self, sender, recipient, message, duration):
        with self.mutex:
            if recipient in self.PO_Boxes.keys():
                msg = ExpiringMessage(sender, message, duration)
                self.PO_Boxes.[recipient].append(msg)
            else:
                print "Attempted to send message to PID: "+ str(PID) + """ which
                does not exist in PostOffice\n"""

    def send_Message(self, sender, recipient, message):        
        msg = ExpiringMessage(sender, message, 0)
        with self.mutex:
            if recipient in self.PO_Boxes.keys():
                self.PO_Boxes[recipient].append(message)
            else:
                print "Attempted to send message to PID: "+ str(PID) + """ which
                does not exist in PostOffice\n"""

    def get_Mail(self, recipient):
        with self.mutex:
            mail = self.PO_Boxes[recipient]
            self.PO_Boxes[recipient] = []
        return mail
