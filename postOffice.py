from expiringObject import ExpiringMessage
import threading

class PostOffice(object):
    """docstring for PostOffice"""

    def __init__(self):
        self.PO_Boxes = {}
        self.addresses = []
        self.mutex = threading.Lock()

    def add_Name(self, PID):
        with self.mutex:
            self.PO_Boxes[PID] = []
            self.addresses.append(PID)
    


    def send_built_Message(sef, sender, recipient, message):
        if sender in self.PO_Boxes and recipient in self.PO_Boxes:
            with self.mutex:
                self.PO_Boxes[recipient].append(message)
        else:
            print "Attempted to send message to PID: "+ str(PID) + """ which
            does not exist in PostOffice\n"""

    def send_Expiring_Message(self, sender, recipient, message, duration): #duration in seconds     
        if sender in self.PO_Boxes and recipient in self.PO_Boxes:
            with self.mutex:
                msg = ExpiringMessage(sender, message, duration)
                self.PO_Boxes[recipient].append(msg)
        else:
            print "Attempted to send message to PID: "+ str(PID) + """ which
            does not exist in PostOffice\n"""

    def send_Message(self, sender, recipient, message):        
        if sender in self.PO_Boxes and recipient in self.PO_Boxes:    
            msg = ExpiringMessage(sender, message, 0)
            with self.mutex:
                self.PO_Boxes[recipient].append(msg)
        else:
            print "Attempted to send message to PID: "+ str(PID) + """ which
            does not exist in PostOffice\n"""

    def get_Mail(self, recipient):
        with self.mutex:
            mail = self.PO_Boxes[recipient]
            self.PO_Boxes[recipient] = []
        return mail

    def get_Mail_From(self, sender, recipient):
        with self.mutex:
            mail_from = [msg for msg in self.PO_Boxes[recipient] if msg.sender == sender]
            self.PO_Boxes[recipient] = [msg for msg in self.PO_Boxes[recipient] if msg.sender != sender]
            return mail_from 