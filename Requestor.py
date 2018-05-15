import requests
import threading

class Requestor(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        with open(r'/home/tme/unlockDoor.txt') as file:
            self.address = file.readline().rstrip('\n')

    def run (self):
        try:
            requests.get(self.address)
        except requests.exceptions.ConnectionError as e:
            print(e)