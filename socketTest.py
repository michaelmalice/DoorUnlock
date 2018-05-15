import socket
from datetime import datetime
from Emailer import Emailer


def CreateSocket(q):
    with open(r'/home/tme/door.txt') as file:
        host = file.readline()
    port = 8686
    q.put(False)

    doorOpenedTime = None
    sendEmail = True

    mySocket = socket.socket()
    try:
        mySocket.connect((host,port))
    except socket.error as e:
        print(e)

    while True:
        if doorOpenedTime is not None:
            if (datetime.now() - doorOpenedTime).total_seconds() > 1800 and sendEmail:
                sendEmail = False
                emailMessage = Emailer()
                emailMessage.start()
        if not q.empty():
            qData = q.get()
            if qData == "exit":
                break
            else:
                q.put(qData)
        mySocket.settimeout(0.1)
        try:
            data = mySocket.recv(1024).decode()
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
            #mySocket.shutdown(socket.SHUT_RDWR)
            mySocket.close()
        except socket.timeout:
            pass


    #mySocket.shutdown(socket.SHUT_RDWR)
    mySocket.close()
    print("Socket Closed")


