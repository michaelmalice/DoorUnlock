import sys
from PyQt4 import QtGui, QtCore
import cv2


class QtCapture(QtGui.QWidget):
    def __init__(self, index, q):
        super(QtGui.QWidget, self).__init__()

        self.fps = 24
        self.cap = cv2.VideoCapture(index)
        self.q = q

        self.video_frame = QtGui.QLabel()
        lay = QtGui.QVBoxLayout()
        lay.setMargin(50)
        lay.addWidget(self.video_frame)
        self.setLayout(lay)

    def setFPS(self, fps):
        self.fps = fps

    def nextFrameSlot(self):
        if not self.q.empty():
            frame = self.q.get()
        #ret, frame = self.cap.read()
        # My webcam yields frames in BGR format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(img)
            pix.scaled(1280, 960)
            self.video_frame.setPixmap(pix)

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000./self.fps)

    def stop(self):
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()


class ControlWindow(QtGui.QWidget):
    def __init__(self, q):
        QtGui.QWidget.__init__(self)

        if q is not None:
            self.capture = QtCapture(0, q)

        self.textbox = QtGui.QLineEdit(self)

        self.quit_button = QtGui.QPushButton('End')
        self.quit_button.clicked.connect(self.endCapture)
        self.end_button = QtGui.QPushButton('Stop')

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.capture)
        self.capture.start()
        self.capture.show()
        vbox.addWidget(self.textbox)
        vbox.addWidget(self.end_button)
        vbox.addWidget(self.quit_button)
        self.setLayout(vbox)
        self.setWindowTitle('Face check-in')
        self.setGeometry(100,100,800,800)
        self.show()

    def startCapture(self):
        if not self.capture:
            self.capture = QtCapture(0)
            self.end_button.clicked.connect(self.capture.stop)
            # self.capture.setFPS(1)
            self.capture.setParent(self)
            self.capture.setWindowFlags(QtCore.Qt.Tool)
        self.capture.start()
        self.capture.show()

    def endCapture(self):
        self.capture.deleteLater()
        self.capture = None

def startGui(q):
    app = QtGui.QApplication(sys.argv)
    window = ControlWindow(q)
    sys.exit(app.exec_())


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    q = None
    window = ControlWindow(q)
    sys.exit(app.exec_())