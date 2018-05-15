import sys
from PyQt4 import QtGui, QtCore

# Window class inherits from QMainWindow
class Window(QtGui.QMainWindow):

    def __init__(self):
        # Calls super __init__ from QMainWindow
        super(Window, self).__init__()
        # Set the window location and size
        self.setGeometry(0, 0, 640, 600)
        # Set the title of the window
        self.setWindowTitle("GUI Test")
        # Assgin an icon for the window in the top left(Doesnt seem to work)
        self.setWindowIcon(QtGui.QIcon('/home/tme/Desktop/Intel.png'))

        # Create options in a menu bar with the name
        extractAction = QtGui.QAction("&GET TO THE CHOPPAH!!!", self)
        # Set a shortcut for the action created
        extractAction.setShortcut("Ctrl+Q")
        # Set infor about the option that appears in the bottom of the window
        extractAction.setStatusTip('Leave The App')
        # Connect the menu bar action to a function
        extractAction.triggered.connect(self.close_application)

        # Creates an action labeled Editor
        openEditor = QtGui.QAction("&Editor", self)
        # Creates a shortcut to trigger the action
        openEditor.setShortcut("Ctrl+E")
        # Creates a status tip that will appear at the bottom of the window when the action is hovered over
        openEditor.setStatusTip('Open Editor')
        # Connect the action to the functin editor
        openEditor.triggered.connect(self.editor)

        # Creates an action labeled Open File
        openFile = QtGui.QAction("&Open File", self)
        # Creates a shortcut to trigger the action
        openFile.setShortcut("Ctrl+O")
        # Creates a status tip that will appear at the bottom of the window when the action is hovered over
        openFile.setStatusTip('Open File')
        # Connect the action to the function file_open
        openFile.triggered.connect(self.file_open)

        # Creates an action labeled Save File
        saveFile = QtGui.QAction("&Save File", self)
        # Creates a shortcut to trigger the action
        saveFile.setShortcut("Ctrl+S")
        # Creates a status tip that will appear at the bottom of the window when the action is hovered over
        saveFile.setStatusTip('Save File')
        # Connect the action to the function file_save
        saveFile.triggered.connect(self.file_save)

        # Create the status bar at the bottom of the window
        self.statusBar()

        # Create the menu bar object, have to do this way for Ubuntu
        mainMenu = QtGui.QMenuBar()
        # Must set native menu bar to false for Ubuntu
        mainMenu.setNativeMenuBar(False)
        # Set the menu bar to the menu bar created above
        self.setMenuBar(mainMenu)
        # Add the file option to the menu bar at the top
        fileMenu = mainMenu.addMenu('&File')
        # Connect the action created above to the button in the menu bar
        fileMenu.addAction(extractAction)

        # Add the openFile action to the menu bar
        fileMenu.addAction(openFile)

        # Add the openFile action to the menu bar
        fileMenu.addAction(saveFile)

        # Add a menu item called Editor
        editorMenu = mainMenu.addMenu("&Editor")
        # Connect the openEditor action to the Editor menu option
        editorMenu.addAction(openEditor)

        # Calls the home funciton
        self.home()

    # The first window to appear when the application is run
    def home(self):
        # Creating a button with the word Quit on it
        btn = QtGui.QPushButton("Quit", self)
        # Connecting the button to a function that will be called when it is clicked
        btn.clicked.connect(self.close_application)

        # Resizing the button to 100 by 100 pixels
        btn.resize(100, 100)
        # Moving the button to 100, 100 from the top left corner
        btn.move(100,100)

        # Creates an action with an icon and text for the toolbar
        extractAction = QtGui.QAction(QtGui.QIcon('Intel.png'), 'Exit Application', self)
        # Connects the action the the close_application function
        extractAction.triggered.connect(self.close_application)

        # Adds a toolbar with an Exit option
        self.toolBar = self.addToolBar("Exit")
        # Connects the extractAction to the Exit toolbar option
        self.toolBar.addAction(extractAction)

        # Creates an action with text for the toolbar
        fontChoice = QtGui.QAction('Font', self)
        # Connects the action to the font_choice function
        fontChoice.triggered.connect(self.font_choice)

        # Adds a toolbar with an Exit option
        # Creates a seperate toolbar from the one created earlier
        #self.toolBar = self.addToolBar("Font")
        # Connects the fontChoice action to the Font toolbar option
        self.toolBar.addAction(fontChoice)

        # Create a color object
        color = QtGui.QColor(0, 0, 0)

        # Create an action for picking a color
        fontColor = QtGui.QAction('Font bg Colo', self)
        # Connect the action to the function color_picker
        fontColor.triggered.connect(self.color_picker)

        # Add the fontColor action to the toolbar
        self.toolBar.addAction(fontColor)

        # Create a checkbox with the text Enlarge Window next to it
        checkBox = QtGui.QCheckBox('Enlarge Window', self)
        # Moves the check box to 200, 200 and sets the size of the object to 300, 50 to show the whole text
        checkBox.setGeometry(200, 200, 300, 50)
        # Sets the checkbox to be toggled on when the window opens, doesnt call the function
        #checkBox.toggle()
        # Connects the enlarge_window function to the checkbox, when state is changed the function is called
        checkBox.stateChanged.connect(self.enlarge_window)

        # Creates a progress bar object
        self.progress = QtGui.QProgressBar(self)
        # moves the progress bar to 200, 80 and sets the size to 250, 20
        self.progress.setGeometry(200, 80, 250, 20)

        # creates a button labeled Download
        self.btn = QtGui.QPushButton("Download", self)
        # Moves the button next to the progress bar
        self.btn.move(200, 120)
        # Connects the button the to the download function defined below
        self.btn.clicked.connect(self.download)

        # Print out the current style type of the GUI
        #print(self.style().objectName())
        # Create a label that says the current style type
        self.styleChoice = QtGui.QLabel(str(self.style().objectName()), self)

        # Create a combo box whixh is a drop down menu
        comboBox = QtGui.QComboBox(self)
        # Add items to the combo box, these are different styles for the GUI
        comboBox.addItem("Windows")
        comboBox.addItem("motif")
        comboBox.addItem("cde")
        comboBox.addItem("Plastique")
        comboBox.addItem("Cleanlooks")

        # Move the combo box to 50, 250
        comboBox.move(50, 250)
        # Move the style choice label to 50, 150
        self.styleChoice.move(50, 150)
        # Connect the combo box to the style_choice function
        comboBox.activated[str].connect(self.style_choice)

        # Create a calendar widget
        cal = QtGui.QCalendarWidget(self)
        # Move the calendar to 500, 200
        cal.move(500, 200)
        # Resize the calendar
        cal.resize(350, 350)


        # Show the created window on the screen
        self.show()

    def file_save(self):
        name = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        file = open(name, 'w')
        text = self.textEdit.toPlainText()
        file.write(text)
        file.close()

    def file_open(self):
        name = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        file = open(name, 'r')

        self.editor()

        with file:
            text = file.read()
            self.textEdit.setText(text)

    # This function prompts the user for a color and then changes the styleChoice label background
    # to that color
    def color_picker(self):
        # Pops up a color picker dialog
        color = QtGui.QColorDialog.getColor()
        # Sets the styleChoice label background to the selected color
        self.styleChoice.setStyleSheet("QWidget { background-color: %s}" % color.name())

    # This function creates a text edit widget and then makes it the central widget
    def editor(self):
        # textEdit is an instance of the object QTextEdit
        self.textEdit = QtGui.QTextEdit()
        # Makes the textEdit widget take up the whole application window
        self.setCentralWidget(self.textEdit)


    # This function pops up a font chooser dialog box and if a valid option is chosen
    #  it changes the font of labels to the given font
    def font_choice(self):
        # Open Font dialog box for choosing
        font, valid = QtGui.QFontDialog.getFont()
        # if valid is True, set the font to the chosen font
        if valid:
            self.styleChoice.setFont(font)


    # This function changes the current style to the given style
    def style_choice(self, text):
        # Change the label to match the chosen style
        self.styleChoice.setText(text)
        # Change the style of the GUI to the given style
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(text))

    # This function simulates the visuals of a download in a progress bar
    def download(self):
        # sets completed to 0
        self.completed = 0
        # keeps running until completed = 100
        while self.completed < 100:
            # adds .0001 to completed each pass
            self.completed += 0.0001
            # sets the value of the progress bar to completed
            self.progress.setValue(self.completed)

    # This function checks the state of the checkbox and sets the window size accordingly
    def enlarge_window(self, state):
        # if the state of the checkbox is checked then set the window to 1280 x 960
        if state == QtCore.Qt.Checked:
            self.setGeometry(0, 0, 1280, 960)
        # if the state of the checkbox is unchecked then set window back to 640 x 480
        else:
            self.setGeometry(0, 0, 640, 480)

    # This function closes the application
    def close_application(self):

        # Creates a Message box with yes and no buttons
        choice = QtGui.QMessageBox.question(self, 'Exit', "Exit the application?",
                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        if choice == QtGui.QMessageBox.Yes:
            print("Exiting Window")
            # Tells the system to kill the process
            sys.exit()
        else:
            pass




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


