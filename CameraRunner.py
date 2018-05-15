import cv2
import webcamPyQTtest
from multiprocessing import Process, Queue

camera_device = cv2.VideoCapture(0)
camera_device.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera_device.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

q = Queue(1)
p = Process(target=webcamPyQTtest.startGui, args=(q,))
p.start()
print("Thread started")

while True:
    ret, frame = camera_device.read()
    if not ret:
        break
    if q.empty():
        q.put(frame)
