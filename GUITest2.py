import sys
from PyQt4 import QtGui, QtCore
import time
from multiprocessing import Process, Queue

# Window class inherits from QMainWindow
class Window(QtGui.QMainWindow):

    def __init__(self):
        # Calls super __init__ from QMainWindow
        super(Window, self).__init__()
        # Set the window location and size
        self.setGeometry(0, 0, 640, 600)
        # Set the title of the window
        self.setWindowTitle("GUI Test 2")
        # Assgin an icon for the window in the top left(Doesnt seem to work)
        self.setWindowIcon(QtGui.QIcon('/home/tme/Desktop/Intel.png'))

        # Calls the home funciton
        self.home()

        self.myThread = updateLabel()
        self.myThread.start()


    def change_label(self, label):
        self.styleChoice.setText(label)

    # The first window to appear when the application is run
    def home(self):


        # Print out the current style type of the GUI
        #print(self.style().objectName())
        # Create a label that says the current style type
        self.styleChoice = QtGui.QLabel(str(self.style().objectName()), self)


        # Show the created window on the screen
        self.show()

class updateLabel(QThread):

    def __init__(self):
        super.__init__()

    def __del__(self):
        self.wait()

    def run(self):
        i = 0
        while True:
            if i == 0:
                self.emit(SIGNAL)
                i += 1
            elif i == 1:
                self.styleChoice.setText("Mr")
                i += 1
            elif i == 2:
                self.styleChoice.setText("President")
                i = 0
            time.sleep(1)



# Main function that runs when the app is started
def run():
    # Creating a QT Application that will hold the window
    app = QtGui.QApplication(sys.argv)
    #Creates an instance of the Window object defined above
    GUI = Window()
    # This line needed for Ubuntu to show the window
    sys.exit(app.exec_())



# Runs the run function to start the application
run()


