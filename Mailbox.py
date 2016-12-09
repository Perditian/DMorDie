"""
 Simple Mailbox/Messaging scheme
 Used as a global Mailbox, coupled with the Game State
 Note: this can be abused to form deadlocks with synchronous messaging (if no
  timeouts)
 
 Messages take the form of (From, To, Message, Sync), where From is the Sender's
  unique ID, To is the receiver's unique ID,
 Message is (usually) a function, and Sync is used for synchronous messages
 Avita Sharma
 11/3/16
 
"""
import threading (or multiprocessing?)
import Queue # something like this, we can use the Queue that supports locks

 class Mailbox:
    def __init__:
        self.__lock = Lock() # used for locking the list of addresses
        self.__queue = Queue()
        self.__addresses = [] # a list of all the people that can use the mailbox
         
    def add_person(Name):
         with self.__lock:
                self.__addresses.append(Name) #NOTE: we can make this a dict to ensure unique IDs
         return
             
    def remove_person(Name):
        with self.__lock:
            self.__addresses.remove(Name)
        return
        
    # asynchronously send a message to one person
    def send_message(From, To, Message):
        self.__queue.add((From, To, Message, None))
                 
    # asynchronously send a message to all people
    def send_message_to_all(From, Message):
        with self.__lock:
            for person in self.__addresses:
                if person != From:
                    self.__queue.add((From, person, Message, None))
        return
                 
     # synchronously send a message to one person and wait for a response, returns the response. TODO: add timeout
     # (Sender_lock may not be necessary)
     def sync_message(From, To, Message, Sender_lock):
         with Sender_lock:
             self.__queue.add((From, To, Message, Message))
             not_found = true
             Reply = None
             while not_found:
                     # iterate through Queue for a message looking like (_, From, _, Message)
                     # once found, set not_found to false, set Reply to the message
         return Reply
             
     # synchronously send a message to all people and wait for a response, returns a list of all responses. 
     # TODO: add timeout (Sender_lock may not be necessary)
     def sync_message_to_all(From, Message, Sender_lock):
            with Sender_lock:
                with self.__lock:
                    for person in self.__addresses:
                        if person != From:
                            self.__queue.add((From, person, Message, Message))
                not_found = true
                Reply = []
                while not_found:
                  # iterate through Queue for messages looking like (To, From, _, Message)
                  # once a message has been received, add it to the Reply list
                  # once all messages have been received, set not_found to false
            return Reply
            
            
       # returns all the messages for a person:
    def get_mail(Person):
        mail = []
        # iterate through Queue looking for messages like (_, Person, _, _)
        # add messages to mail
        return mail
     
     
         
