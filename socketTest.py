import socket
from datetime import datetime
from Emailer import Emailer

# The CreateSocket function takes a Queue object to allow the transfer of information back and forth between threads
# The CreateSocket function checks the Pi to see if the door has been opened.
# If the door is open then tells the main thread the door is open through the Queue
def CreateSocket(q):
    # Read the IP address of the door
    with open(r'/home/tme/door.txt') as file:
        host = file.readline()
    port = 8686
    q.put(False)

    doorOpenedTime = None
    sendEmail = True

    # Create a socket item
    mySocket = socket.socket()
    # Try to connect to the socket server running on the Pi
    try:
        mySocket.connect((host,port))
    except socket.error as e:
        print(e)
    # Loop forever checking the socket for messages
    while True:
        if doorOpenedTime is not None:
            if (datetime.now() - doorOpenedTime).total_seconds() > 1800 and sendEmail:
                sendEmail = False
                emailMessage = Emailer()
                emailMessage.start()
        # Check the Queue to see if it has information, if it does check to see if it says exit.
        # If the Queue says exit then break the loop
        if not q.empty():
            qData = q.get()
            if qData == "exit":
                break
            else:
                q.put(qData)
        # Set receive listen timeout to 1/10 of a second so it doesn't hang forever waiting for a message
        mySocket.settimeout(0.1)
        # Try to receive data from the socket, if it times out pass and run loop again
        try:
            data = mySocket.recv(1024).decode()
            # If data is None then the socket server isn't running and break the loop
            if not data:
                break
            print("from connected  user: " + str(data))

            if data == "opened":
                if q.empty():
                    q.put(True)

                else:
                    qData = q.get()
                    if qData == "exit":
                        break
                    q.put(True)
                doorOpenedTime = datetime.now()
                print("Door opened at " + str(doorOpenedTime))
            elif data == "closed":
                if q.empty():
                    q.put(False)
                else:
                    qData = q.get()
                    if qData == "exit":
                        print("quitting")
                        break
                    q.put(False)
                sendEmail = True
                doorOpenedTime = None
                print("Door closed")
        except KeyboardInterrupt:
            print("Kayboard interrupt detected. Closing Socket.")
            mySocket.close()
        except socket.timeout:
            pass


    mySocket.close()
    print("Socket Closed")


