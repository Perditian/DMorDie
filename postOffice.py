"""
 Avita Sharma, Eric Wyss, Davis Taus
 Post Office Class, handles messaging between threads
 Messages are Expiring Messages
"""
from expiringObject import ExpiringMessage
import threading

class PostOffice(object):
    
    def __init__(self):
        self.PO_Boxes = {}
        self.addresses = []
        self.mutex = threading.Lock()

    # Add a name to the Post Office:
    def add_Name(self, PID):
        with self.mutex:
            self.PO_Boxes[PID] = []
            self.addresses.append(PID)
    
    # Send an already built expiring message:
    def send_built_Message(self, sender, recipient, message):
        if sender in self.PO_Boxes and recipient in self.PO_Boxes:
            with self.mutex:
                self.PO_Boxes[recipient].append(message)
        else:
            print ("Attempted to send message to PID: "+ str(PID) + \
                   " which does not exist in PostOffice\n")

    # Send a message which will expire in duration seconds:
    def send_Expiring_Message(self, sender, recipient, message, duration):
        if sender in self.PO_Boxes and recipient in self.PO_Boxes:
            with self.mutex:
                msg = ExpiringMessage(sender, message, duration)
                self.PO_Boxes[recipient].append(msg)
        else:
            print ("Attempted to send message to PID: "+ str(PID) + \
                   " which does not exist in PostOffice\n")

    # Send a message which will never expire:
    def send_Message(self, sender, recipient, message):        
        if sender in self.PO_Boxes and recipient in self.PO_Boxes:    
            msg = ExpiringMessage(sender, message, 0)
            with self.mutex:
                self.PO_Boxes[recipient].append(msg)
        else:
            print ("Attempted to send message to PID: "+ str(PID) + \
                   " which does not exist in PostOffice\n")

    # get all mail from the recipient's mailbox:
    def get_Mail(self, recipient):
        with self.mutex:
            mail = self.PO_Boxes[recipient]
            self.PO_Boxes[recipient] = []
        return mail

    # get all mail from recipient that was sent by sender:
    def get_Mail_From(self, sender, recipient):
        with self.mutex:
            mail_from = [msg for msg in self.PO_Boxes[recipient] \
                             if msg.sender == sender]
            self.PO_Boxes[recipient] = [msg for msg in \
                                            self.PO_Boxes[recipient] \
                                            if msg.sender != sender]
            return mail_from 