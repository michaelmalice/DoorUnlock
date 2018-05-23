#! /usr/bin/env python3

# Copyright(c) 2017 Intel Corporation.
# License: MIT See LICENSE file in root directory.
#Test


from mvnc import mvncapi as mvnc
import numpy
import cv2
import sys
import os
import requests
import datetime
from Emailer import Emailer
from Requestor import Requestor
from socketTest import CreateSocket
#from ThreadedHTTPTest import startThread
#from ThreadedHTTPTest import ReedHandler
from subprocess import call
from subprocess import Popen
from multiprocessing import Process, Queue
import time
from datetime import datetime

EXAMPLES_BASE_DIR='../../'
IMAGES_DIR = '/home/tme/Desktop/'

VALIDATED_IMAGES_DIR = IMAGES_DIR + 'validated_images/'
#validated_image_filename = VALIDATED_IMAGES_DIR + 'valid1.jpg'

GRAPH_FILENAME = "facenet_celeb_ncs.graph"

#entrants = ["Michael Larsen", "Dmitry Ivanov", "Art Webb", "Lucas Ainsworth"]


# name of the opencv window
CV_WINDOW_NAME = "FaceNet"

CAMERA_INDEX = 0
REQUEST_CAMERA_WIDTH = 640
REQUEST_CAMERA_HEIGHT = 480
REQUEST_CAMERA_FPS = 5

# the same face will return 0.0
# different faces return higher numbers
# this is NOT between 0.0 and 1.0
FACE_MATCH_THRESHOLD = 0.7

# labels for objects. The class IDs returned are the indices into this list
labels = ('background',
          'aeroplane', 'bicycle', 'bird', 'boat',
          'bottle', 'bus', 'car', 'cat', 'chair',
          'cow', 'diningtable', 'dog', 'horse',
          'motorbike', 'person', 'pottedplant',
          'sheep', 'sofa', 'train', 'tvmonitor')

# the minimal score for a box to be shown
min_score_percent = 60

# Variables for Recording
noPerson = None
startRecord = True
dirName = '/media/isos/Recordings'
killSwitch = False
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = None
record = False


# Run an inference on the passed image
# image_to_classify is the image on which an inference will be performed
#    upon successful return this image will be overlayed with boxes
#    and labels identifying the found objects within the image.
# ssd_mobilenet_graph is the Graph object from the NCAPI which will
#    be used to peform the inference.
def run_inference(image_to_classify, facenet_graph, input_fifo, output_fifo):

    # get a resized version of the image that is the dimensions
    # SSD Mobile net expects
    resized_image = preprocess_image(image_to_classify)

    # Create Tensor for the inference
    tensor = resized_image.astype(numpy.float16)

    # Write the tensor to the input_fifo and queue an inference
    facenet_graph.queue_inference_with_fifo_elem(input_fifo, output_fifo, tensor, 'user object')

    # Read the results from the queue
    output, user_obj = output_fifo.read_elem()
    print("Read from movidius successful")




    return output

    # Run an inference on the passed image
    # image_to_classify is the image on which an inference will be performed
    #    upon successful return this image will be overlayed with boxes
    #    and labels identifying the found objects within the image.
    # ssd_mobilenet_graph is the Graph object from the NCAPI which will
    #    be used to peform the inference.
def run_inference2(image_to_classify, ssd_mobilenet_graph, input_fifo, output_fifo):


    # importing global variables
    global noPerson
    global startRecord
    global dirName
    global killSwitch
    global fourcc
    global out
    global record

    # preprocess the image to meet nework expectations
    resized_image = preprocess_image2(image_to_classify)

    # Create Tensor for the inference
    tensor = resized_image.astype(numpy.float16)

    # Write the tensor to the input_fifo and queue an inference
    ssd_mobilenet_graph.queue_inference_with_fifo_elem(input_fifo, output_fifo, tensor, 'user object')

    # Read the results from the Queue
    output, user_obj = output_fifo.read_elem()
    print("Read from movidius successful")

    #   a.	First fp16 value holds the number of valid detections = num_valid.
    #   b.	The next 6 values are unused.
    #   c.	The next (7 * num_valid) values contain the valid detections data
    #       Each group of 7 values will describe an object/box These 7 values in order.
    #       The values are:
    #         0: image_id (always 0)
    #         1: class_id (this is an index into labels)
    #         2: score (this is the probability for the class)
    #         3: box left location within image as number between 0.0 and 1.0
    #         4: box top location within image as number between 0.0 and 1.0
    #         5: box right location within image as number between 0.0 and 1.0
    #         6: box bottom location within image as number between 0.0 and 1.0

    # number of boxes returned
    num_valid_boxes = int(output[0])

    for box_index in range(num_valid_boxes):
        base_index = 7 + box_index * 7
        if (not numpy.isfinite(output[base_index]) or
                not numpy.isfinite(output[base_index + 1]) or
                not numpy.isfinite(output[base_index + 2]) or
                not numpy.isfinite(output[base_index + 3]) or
                not numpy.isfinite(output[base_index + 4]) or
                not numpy.isfinite(output[base_index + 5]) or
                not numpy.isfinite(output[base_index + 6])):
            # boxes with non finite (inf, nan, etc) numbers must be ignored
            continue

        x1 = max(int(output[base_index + 3] * image_to_classify.shape[0]), 0)
        y1 = max(int(output[base_index + 4] * image_to_classify.shape[1]), 0)
        x2 = min(int(output[base_index + 5] * image_to_classify.shape[0]), image_to_classify.shape[0] - 1)
        y2 = min((output[base_index + 6] * image_to_classify.shape[1]), image_to_classify.shape[1] - 1)

        # overlay boxes and labels on to the image
        overlaid = overlay_on_image2(image_to_classify, output[base_index:base_index + 7])
        if overlaid:
            record = True
            noPerson = None
        if not overlaid and noPerson == None and record:
            noPerson = datetime.now()

        if (record):
            if startRecord:
                startRecord = False
                out = cv2.VideoWriter(os.path.join(dirName, str(datetime.now())) + ".avi", fourcc,
                                               7.0, (640, 480), True)
            out.write(image_to_classify)
            if noPerson != None:
                if (datetime.now() - noPerson).total_seconds() >= 3:
                    out.release()
                    record = False
                    startRecord = True

        # if (overlaid == False and capture == True):
        # print("early stop")
        # sendEmailMessage(dirName)
        # capture = False
        # dirName = ''


# overlays the boxes and labels onto the display image.
# display_image is the image on which to overlay to
# image info is a text string to overlay onto the image.
# matching is a Boolean specifying if the image was a match.
# returns None
def overlay_on_image(display_image, image_info, matching, user):
    rect_width = 10
    offset = int(rect_width/2)
    if (image_info != None):
        #cv2.putText(display_image, image_info, (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        #cv2.putText(display_image, "Chun Le", (30, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 0)
        if (matching != 2):
            cv2.rectangle(display_image, (180, 420), (445, 460), (255, 255, 255), -1)
            cv2.putText(display_image, "Place Face Here", (180, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        #testing

    if (matching == 1):
        # match, green rectangle
        cv2.rectangle(display_image, (0+offset, 0+offset),
                      (display_image.shape[1]-offset-1, display_image.shape[0]-offset-1),
                      (0, 255, 0), 10)
    elif (matching == 2):
        # match, green rectangle
        cv2.rectangle(display_image, (0+offset, 0+offset),
                      (display_image.shape[1]-offset-1, display_image.shape[0]-offset-1),
                      (0, 255, 0), 10)
        cv2.rectangle(display_image, (125, 360), (510, 470), (255, 255, 255), -1)
        cv2.putText(display_image, "Checked In", (138, 410), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
        cv2.putText(display_image, user, (125, 460), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
    else:
        # not a match, red rectangle
        cv2.rectangle(display_image, (0+offset, 0+offset),
                      (display_image.shape[1]-offset-1, display_image.shape[0]-offset-1),
                      (0, 0, 255), 10)

    # overlays the boxes and labels onto the display image.
    # display_image is the image on which to overlay the boxes/labels
    # object_info is a list of 7 values as returned from the network
    #     These 7 values describe the object found and they are:
    #         0: image_id (always 0 for myriad)
    #         1: class_id (this is an index into labels)
    #         2: score (this is the probability for the class)
    #         3: box left location within image as number between 0.0 and 1.0
    #         4: box top location within image as number between 0.0 and 1.0
    #         5: box right location within image as number between 0.0 and 1.0
    #         6: box bottom location within image as number between 0.0 and 1.0
    # returns None
def overlay_on_image2(display_image, object_info):

    source_image_width = display_image.shape[1]
    source_image_height = display_image.shape[0]

    base_index = 0
    class_id = object_info[base_index + 1]
    percentage = int(object_info[base_index + 2] * 100)
    if (percentage <= min_score_percent or int(class_id) != 15):
        return False
    label_text = labels[int(class_id)] + " (" + str(percentage) + "%)"
    box_left = int(object_info[base_index + 3] * source_image_width)
    box_top = int(object_info[base_index + 4] * source_image_height)
    box_right = int(object_info[base_index + 5] * source_image_width)
    box_bottom = int(object_info[base_index + 6] * source_image_height)

    box_color = (255, 128, 0)  # box color
    box_thickness = 2
    cv2.rectangle(display_image, (box_left, box_top), (box_right, box_bottom), box_color, box_thickness)

    scale_max = (100.0 - min_score_percent)
    scaled_prob = (percentage - min_score_percent)
    scale = scaled_prob / scale_max

    # draw the classification label string just above and to the left of the rectangle
    # label_background_color = (70, 120, 70)  # greyish green background for text
    label_background_color = (0, int(scale * 175), 75)
    label_text_color = (255, 255, 255)  # white text

    label_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    label_left = box_left
    label_top = box_top - label_size[1]
    if (label_top < 1):
        label_top = 1
    label_right = label_left + label_size[0]
    label_bottom = label_top + label_size[1]
    cv2.rectangle(display_image, (label_left - 1, label_top - 1), (label_right + 1, label_bottom + 1),
                    label_background_color, -1)

    # label text above the box
    cv2.putText(display_image, label_text, (label_left, label_bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                label_text_color, 1)

    # display text to let user know how to quit
    cv2.rectangle(display_image, (0, 0), (100, 15), (128, 128, 128), -1)
    cv2.putText(display_image, "Q to Quit", (10, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    return True

# whiten an image
def whiten_image(source_image):
    source_mean = numpy.mean(source_image)
    source_standard_deviation = numpy.std(source_image)
    std_adjusted = numpy.maximum(source_standard_deviation, 1.0 / numpy.sqrt(source_image.size))
    whitened_image = numpy.multiply(numpy.subtract(source_image, source_mean), 1 / std_adjusted)
    return whitened_image

# create a preprocessed image from the source image that matches the
# network expectations and return it
def preprocess_image(src):
    # scale the image
    NETWORK_WIDTH = 160
    NETWORK_HEIGHT = 160
    preprocessed_image = cv2.resize(src, (NETWORK_WIDTH, NETWORK_HEIGHT))

    #convert to RGB
    preprocessed_image = cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2RGB)

    #whiten
    preprocessed_image = whiten_image(preprocessed_image)

    # return the preprocessed image
    return preprocessed_image

    # create a preprocessed image from the source image that complies to the
    # network expectations and return it
def preprocess_image2(source_image):
    # the ssd mobilenet image width and height
    NETWORK_IMAGE_WIDTH = 300
    NETWORK_IMAGE_HEIGHT = 300
    resized_image = cv2.resize(source_image, (NETWORK_IMAGE_WIDTH, NETWORK_IMAGE_HEIGHT))

    # trasnform values from range 0-255 to range -1.0 - 1.0
    resized_image = resized_image - 127.5
    resized_image = resized_image * 0.007843
    return resized_image

# determine if two images are of matching faces based on the
# the network output for both images.
def face_match(faces_output, face2_output):
    for face in faces_output:
        if (len(faces_output[face]) != len(face2_output)):
            print('length mismatch in face_match')
            return False
        total_diff = 0
        for output_index in range(0, len(faces_output[face])):
            this_diff = numpy.square(faces_output[face][output_index] - face2_output[output_index])
            total_diff += this_diff
        #print('Total Difference is: ' + str(total_diff))

        if (total_diff < FACE_MATCH_THRESHOLD):
            # the total difference between the two is under the threshold so
            # the faces match.
            return face

    # differences between faces was over the threshold above so
    # they didn't match.
    return False

# handles key presses
# raw_key is the return value from cv2.waitkey
# returns False if program should end, or True if should continue
def handle_keys(raw_key):
    ascii_code = raw_key & 0xFF
    if ((ascii_code == ord('q')) or (ascii_code == ord('Q'))):
        return False
    elif ((ascii_code == ord('p')) or (ascii_code == ord('P'))):
        return 2
    else:
        return True


# start the opencv webcam streaming and pass each frame
# from the camera to the facenet network for an inference
# Continue looping until the result of the camera frame inference
# matches the valid face output and then return.
# valid_output is inference result for the valid image
# validated image filename is the name of the valid image file
# graph is the ncsdk Graph object initialized with the facenet graph file
#   which we will run the inference on.
# returns None
def run_camera(valid_output, graph, graph2, input_fifo_face, output_fifo_face, input_fifo_ssd, output_fifo_ssd):
    camera_device = cv2.VideoCapture(CAMERA_INDEX)
    camera_device.set(cv2.CAP_PROP_FRAME_WIDTH, REQUEST_CAMERA_WIDTH)
    camera_device.set(cv2.CAP_PROP_FRAME_HEIGHT, REQUEST_CAMERA_HEIGHT)
    camera_device.set(cv2.CAP_PROP_FPS, REQUEST_CAMERA_FPS)

    actual_camera_width = camera_device.get(cv2.CAP_PROP_FRAME_WIDTH)
    actual_camera_height = camera_device.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print ('actual camera resolution: ' + str(actual_camera_width) + ' x ' + str(actual_camera_height))

    if ((camera_device == None) or (not camera_device.isOpened())):
        print ('Could not open camera.  Make sure it is plugged in.')
        print ('Also, if you installed python opencv via pip or pip3 you')
        print ('need to uninstall it and install from source with -D WITH_V4L=ON')
        print ('Use the provided script: install-opencv-from_source.sh')
        return

    frame_count = 0

    #entrant = 0

    cv2.namedWindow(CV_WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(CV_WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    found_match = 0

    Faked = False
    match_count = 0
    global out
    global record
    global startRecord

    q = Queue(1)
    p = Process(target=CreateSocket, args=(q,))
    p.start()
    print("Thread created")

    while True :
        # Read image from camera,
        ret_val, vid_image = camera_device.read()
        if not ret_val:
            print("No image from camera, exiting")
            break

        frame_count += 1
        frame_name = 'camera frame ' + str(frame_count)

        if not q.empty():
            doorOpen = q.get()

        if (not doorOpen):
            if out != None:
                if out.isOpened():
                    out.release()
                    startRecord = True
            record = False
            match_count = CheckFace(valid_output,vid_image, graph, CV_WINDOW_NAME,
                                    match_count, input_fifo_face, output_fifo_face)

        elif (doorOpen):
            match_count = 0
            run_inference2(vid_image, graph2, input_fifo_ssd, output_fifo_ssd)


        # check if the window is visible, this means the user hasn't closed
        # the window via the X button
        prop_val = cv2.getWindowProperty(CV_WINDOW_NAME, cv2.WND_PROP_ASPECT_RATIO)
        if (prop_val < 0.0):
            print('window closed')
            break

        # display the results and wait for user to hit a key
        cv2.imshow(CV_WINDOW_NAME, vid_image)
        raw_key = cv2.waitKey(1)
        if raw_key != -1:
            if handle_keys(raw_key) == False:
                print('user pressed Q')
                if q.empty():
                    q.put("exit")
                else:
                    q.get()
                    q.put("exit")
                break

    camera_device.release()


def CheckFace(valid_output, vid_image, graph, frame_name, match_count, input_fifo, output_fifo):


    # run a single inference on the image and overwrite the
    # boxes and labels
    test_output = run_inference(vid_image, graph, input_fifo, output_fifo)

    matched_face = face_match(valid_output, test_output)
    if (matched_face != False):

        print('PASS!  File ' + matched_face + ' matches ')
        match_count += 1
        if (match_count >= 5 and match_count <= 7):
            print('User Checked In!')
            found_match = 2
            if (match_count == 7):
                match_count = 0
                Requestor().start()
                excemptions = ['Michael', 'Chris L']
                if matched_face not in excemptions:
                    fileName = '/home/tme/Desktop/Log/' + matched_face + str(datetime.now()) + '.png'
                    cv2.imwrite(fileName, vid_image)
                    emailMessage = Emailer(fileName, matched_face)
                    emailMessage.start()

        else:
            found_match = 1

    else:
        found_match = 3
        # print('FAIL!  File ' + frame_name + ' does not match ')
        match_count = 0
        # Uncomment next line to view the image sent to the graph
        # vid_image = preprocess_image(vid_image)


    overlay_on_image(vid_image, frame_name, found_match, matched_face)
    return match_count

# This function is called from the entry point to do
# all the work of the program
def main():

    ENTRANT = 0
    # Get a list of ALL the sticks that are plugged in
    # we need at least one
    devices = mvnc.enumerate_devices()
    if len(devices) == 0:
        print('No NCS devices found')
        quit()

    # Pick the first stick to run the FaceNetwork
    device = mvnc.Device(devices[0])

    #Pick the second stick to run the Person Detector
    #device2 = mvnc.Device(devices[1])

    # Open the first NCS
    device.open()

    # Open the second NCS
    #device2.OpenDevice()

    # The graph file that was created with the ncsdk compiler
    graph_file_name = GRAPH_FILENAME
    graph2 = 'graph'

    # read in the graph file to memory buffer
    with open(graph_file_name, mode='rb') as f:
        graph_in_memory = f.read()

    with open(graph2, mode='rb') as f:
        graph_data = f.read()

    # create the NCAPI graph instance from the memory buffer containing the graph file.
    graph = mvnc.Graph('graph_in_memory')

    # allocate the Graph instance from NCAPI by passing the memory buffer
    ssd_mobilenet_graph = mvnc.Graph("graph_data")

    # Create input and output for face_graph
    input_fifo, output_fifo = graph.allocate_with_fifos(device, graph_in_memory)

    #Create input and output for ssd_graph
    input_fifo_ssd, output_fifo_ssd = ssd_mobilenet_graph.allocate_with_fifos(device, graph_data)

    valid_output = {}

    for root, dirs, files in os.walk(VALIDATED_IMAGES_DIR):
        for file in files:
            if file[-4:] == ".jpg" or file[-4:] == ".png":
                validated_image_filename = VALIDATED_IMAGES_DIR + file
                validated_image = cv2.imread(validated_image_filename)
                valid_output[file[:-4]] = run_inference(validated_image, graph, input_fifo, output_fifo)

    #http_thread = ThreadedHTTP(('', 8686), ReedHandler)



    run_camera(valid_output, graph, ssd_mobilenet_graph, input_fifo, output_fifo, input_fifo_ssd, output_fifo_ssd)


    # Clean up the graph and the device
    input_fifo.destroy()
    input_fifo_ssd.destroy()
    output_fifo.destroy()
    output_fifo_ssd.destroy()
    graph.destroy()
    ssd_mobilenet_graph.destroy()
    device.close()
    device.destroy()
    #device2.CloseDevice()



# main entry point for program. we'll call main() to do what needs to be done.
if __name__ == "__main__":
    sys.exit(main())
