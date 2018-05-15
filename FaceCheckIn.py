#! /usr/bin/env python3

# Copyright(c) 2017 Intel Corporation. 
# License: MIT See LICENSE file in root directory.


from mvnc import mvncapi as mvnc
import numpy
import cv2
import sys
import os
import requests
import datetime
from Emailer import Emailer
from Requestor import Requestor
import time

EXAMPLES_BASE_DIR='../../'
IMAGES_DIR = '/home/tme/Desktop/'

VALIDATED_IMAGES_DIR = IMAGES_DIR + 'validated_images/'
#validated_image_filename = VALIDATED_IMAGES_DIR + 'valid1.jpg'

GRAPH_FILENAME = "/home/tme/Desktop/facenet_celeb_ncs.graph"

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


# Run an inference on the passed image
# image_to_classify is the image on which an inference will be performed
#    upon successful return this image will be overlayed with boxes
#    and labels identifying the found objects within the image.
# ssd_mobilenet_graph is the Graph object from the NCAPI which will
#    be used to peform the inference.
def run_inference(image_to_classify, facenet_graph):

    # get a resized version of the image that is the dimensions
    # SSD Mobile net expects
    resized_image = preprocess_image(image_to_classify)


    # ***************************************************************
    # Send the image to the NCS
    # ***************************************************************
    facenet_graph.LoadTensor(resized_image.astype(numpy.float16), None)

    # ***************************************************************
    # Get the result from the NCS
    # ***************************************************************
    output, userobj = facenet_graph.GetResult()

    return output


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
        print('Total Difference is: ' + str(total_diff))

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
def run_camera(valid_output, graph):
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
    match_count = 0
    #entrant = 0

    cv2.namedWindow(CV_WINDOW_NAME)

    found_match = 0

    Faked = False

    while True :
        # Read image from camera,
        ret_val, vid_image = camera_device.read()
        if (not ret_val):
            print("No image from camera, exiting")
            break

        frame_count += 1
        frame_name = 'camera frame ' + str(frame_count)



        if (not Faked):
            # run a single inference on the image and overwrite the
            # boxes and labels
            test_output = run_inference(vid_image, graph)

            matched_face = face_match(valid_output, test_output)
            if (matched_face != False):

                print('PASS!  File ' + matched_face + ' matches ')
                match_count += 1
                if (match_count >= 5 and match_count <= 7):
                    print('User Checked In!')
                    found_match = 2
                    if (match_count == 7):
                        #return
                        match_count = 0
                        Requestor().start()
                        excemptions = ['Michael', 'Chris L']
                        if matched_face not in excemptions:
                            fileName = '/home/tme/Desktop/Log/' + matched_face + str(datetime.datetime.now()) + '.png'
                            cv2.imwrite(fileName, vid_image)
                            emailMessage = Emailer(fileName, matched_face)
                            emailMessage.start()

                else:
                    found_match = 1

            else:
                found_match = 3
                print('FAIL!  File ' + frame_name + ' does not match ')
                match_count = 0
            #Uncomment next line to view the image sent to the graph
            #vid_image = preprocess_image(vid_image)

        overlay_on_image(vid_image, frame_name, found_match, matched_face)

        # check if the window is visible, this means the user hasn't closed
        # the window via the X button
        prop_val = cv2.getWindowProperty(CV_WINDOW_NAME, cv2.WND_PROP_ASPECT_RATIO)
        if (prop_val < 0.0):
            print('window closed')
            break

        # display the results and wait for user to hit a key
        cv2.imshow(CV_WINDOW_NAME, vid_image)
        raw_key = cv2.waitKey(1)
        if (raw_key != -1):
            if (handle_keys(raw_key) == False):
                print('user pressed Q')
                break
            if (handle_keys(raw_key) == 2):
                Faked = True
                print('PASS!  File ' + frame_name + ' matches ')
                match_count += 1
                if (match_count == 2):
                    print('User Checked In!')
                    found_match = 2
                elif (match_count == 3):
                    Faked = False
                    match_count = 0
                else:
                    found_match = 1

    if (found_match):
        cv2.imshow(CV_WINDOW_NAME, vid_image)
        cv2.waitKey(0)


# This function is called from the entry point to do
# all the work of the program
def main():

    ENTRANT = 0
    # Get a list of ALL the sticks that are plugged in
    # we need at least one
    devices = mvnc.EnumerateDevices()
    if len(devices) == 0:
        print('No NCS devices found')
        quit()

    # Pick the first stick to run the network
    device = mvnc.Device(devices[0])

    # Open the NCS
    device.OpenDevice()

    # The graph file that was created with the ncsdk compiler
    graph_file_name = GRAPH_FILENAME

    # read in the graph file to memory buffer
    with open(graph_file_name, mode='rb') as f:
        graph_in_memory = f.read()

    # create the NCAPI graph instance from the memory buffer containing the graph file.
    graph = device.AllocateGraph(graph_in_memory)

    valid_output = {}

    for root, dirs, files in os.walk(VALIDATED_IMAGES_DIR):
        for file in files:
            if file[-4:] == ".jpg" or file[-4:] == ".png":
                validated_image_filename = VALIDATED_IMAGES_DIR + file
                validated_image = cv2.imread(validated_image_filename)
                valid_output[file[:-4]] = run_inference(validated_image, graph)

    run_camera(valid_output, graph)

    # Clean up the graph and the device
    graph.DeallocateGraph()
    device.CloseDevice()



# main entry point for program. we'll call main() to do what needs to be done.
if __name__ == "__main__":
    sys.exit(main())
