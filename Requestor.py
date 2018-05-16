import requests
import threading

# The Requestor class inherits from the Thread class so it can be run without holding the main thread
# The Requestor class sends a web request to the Raspberry Pi telling it to run the servo and open the door
class Requestor(threading.Thread):

    # Read the URL of the server running on the Pi from a text file
    def __init__(self):
        threading.Thread.__init__(self)
        with open(r'/home/tme/unlockDoor.txt') as file:
            self.address = file.readline().rstrip('\n')

    # The run function is called when the thread is started, it sends a request to the Pi to open the door
    def run (self):
        try:
            requests.get(self.address)
        except requests.exceptions.ConnectionError as e:
            print(e)