from imutils.video import VideoStream
import time
import cv2
import os
import numpy
import datetime
import argparse
import json
import vlc

conf = json.load(open("Stopmotion.json"))

def LoadConfigFile():
    global conf
    conf = json.load(open("Stopmotion.json"))
    print ("Config File Reloaded")
    return conf

def Playsound():
    if conf["PlaySound"] == True:
        p = vlc.MediaPlayer("C:\Git\openCV\Sounds\CameraClick.mp3")
        p.play()
    else:
        print("sound not activated - picture taken")

def ShowVideoOutput(LiveFeed, frameDelta, thresh, firstFrame):
    if conf["ShowPictures"] == True:
        cv2.imshow("Live View", LiveFeed)
        cv2.imshow("Frame Delta", frameDelta)
        cv2.imshow("Thresholded View", thresh)
        cv2.imshow("Background substraction base", firstFrame)

def CloseCamera(camera):
    # a function to ensure camera is properly closed and all display windows are removed
    cv2.destroyAllWindows()
    #vs.stop()
    print ("[Camera Status] - deactivated")
    camera.release()

def RecordVideo(camera):
    # a function to record a video for later off-line analysis
    VideoName = input("VideoName (without extension) : ")                                                           # ask for filename
    if os.path.isfile("C:\Git\openCV\Videos"+chr(92)+ format(VideoName)+'.avi'):                                                      # check if file exists
        Selection = input("File exists! Overwrite? (y/n) :")                                                        # ask to overwrite in case the file is already existing
        if Selection.lower() == "y":                                                                                    # if overwrite was chosen,
            os.remove("C:\Git\openCV\Videos"+chr(92)+ format(VideoName)+'.avi')                                                       # delete the file
        else:                                                                                                           # if overwrite was not chosen,
            RecordVideo(camera)                                                                                         # restart function and re-ask for the name

    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')                                                                 # Define the codec and create VideoWriter object
    RecordedVideo = cv2.VideoWriter("C:\Git\openCV\Videos"+chr(92)+ format(VideoName) + '.avi', fourcc, 25, (640, 480), True)         # Define the Video parameters (name, resolution, framerate)
    #camera = vs.read()

    while True:                                                                                                         # loop over frames from camera
        grabbed, LiveFeed = camera.read()                                                                                   # read single frame from camera
        #LiveFeed = imutils.resize(LiveFeed, width=500)
        if grabbed == True:                                                                                                 # as long as there is a frame,
            RecordedVideo.write(LiveFeed)                                                                               # add this frame to the defined video stream
            cv2.putText(LiveFeed, "Recording file .."+chr(92)+"C:\Git\openCV\Videos"+chr(92)+ format(VideoName)+'.avi',               # for the live view, add an identifier that the video is recorded
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 2)
            cv2.imshow('Recorder', LiveFeed)                                                                            # and show the frame as live view
            if cv2.waitKey(1) & 0xFF == 27:                                                                             # when ESC button was pressed,
                CloseCamera(camera)                                                                                     # call the camera close function
                RecordedVideo.release()                                                                                 # and release the recorded video file to ensure this is properly stored
                break                                                                                                   # go back to main menu
        else:                                                                                                           # if camera hardware is closed externally(for any reason, e.g. USB unplugged)
            CloseCamera(camera)                                                                                         # call the camera close function
            RecordedVideo.release()                                                                                     # and release the recorded video file to ensure this is properly stored
            break                                                                                                       # go back to main menu
    return camera

def CreateStopMotionVideo():
    # choose codec according to format needed
    #fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    #video = cv2.VideoWriter('C:\Git\openCV\Videos\StopMotion.avi', fourcc, 1, (conf["ResolutionW"], conf["ResolutionH"]))

    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # Define the codec and create VideoWriter object
    video = cv2.VideoWriter("C:\Git\openCV\Videos\StopMotion.avi", fourcc, 1,(conf["ResolutionW"], conf["ResolutionH"]), True)

    for j in range(1, 9):
        image ="C:\Git\openCV\Screenshots\StopMotion"+str(j) + ".jpg"
        img = cv2.imread(str(image))
        print("reading "+str(image))
        cv2.imshow('Recorder', img)
        time.sleep(1)
        video.write(img)

    cv2.destroyAllWindows()
    video.release()

def CameraCalibration(camera):
    # a function which allows to calibrate the camera orientation before recording or live tracking is started
    while(camera.isOpened()):                                                                                           # loop over frames from camera
        grabbed, LiveFeed = camera.read()                                                                                   # read single frame from camera
        if grabbed==True:                                                                                                   # as long as there is a frame,
            cv2.imshow('Calibration Window - press ESC to finalize',LiveFeed)                                                                   # and show the frame as live view
            if cv2.waitKey(1) & 0xFF == 27:                                                                             # when ESC button was pressed,
                print ("calibration finished")
                #cv2.imwrite('static\images\Calibration.jpg', LiveFeed)
                CloseCamera(camera)                                                                                     # call the camera close function
                break
            elif cv2.waitKey(1) & 0xFF == ord("f"):
                LoadConfigFile()
        else:
            CloseCamera(camera)                                                                                         # call the camera close function
            print ("camera not active")
            break                                                                                                       # go back to main menu
    return camera

def OfflineVideo():
    # a function to initialize an pre-recorded video for offfline analysis
    print ("All *.avi files in .."+chr(92)+"C:\Git\openCV\Videos"+chr(92)+":")
    for file in os.listdir("C:\Git\openCV\Videos"):                                                                           # show the content of the videos folder
        if "avi" in file:                                                                                               # only print avi files
            print (file)
    Selection = input("select file to play (without extension): ")                                                  # ask user to type in the file to play
    if Selection=="":                                                                                                   # if nothing is entered
        camera = cv2.VideoCapture("C:\Git\openCV\Videos" + chr(92) + "Video_oneobj_2" + ".avi")                                      # take the default video
    else:
        if os.path.isfile("C:\Git\openCV\Videos"+chr(92)+Selection+".avi"):                                                           # check if the file is existing
            camera = cv2.VideoCapture("C:\Git\openCV\Videos"+chr(92)+Selection+".avi")                                                # take the file defined by the user if it is existing in the video folder
            print  ("Selected file: " + str(camera))
        else:
            print ("file not found!")                                                                                    # if file was not found,
            OfflineVideo()                                                                                              # restart function and re-ask for name
    return camera

def OnlineVideo():
    # a function to define the standard camera hardware as video source

    #vs = VideoStream(usePiCamera=0, resolution=(800, 600)).start()

    print ("[Camera Status] - warming up")
    time.sleep(1.0)
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, conf["ResolutionW"])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, conf["ResolutionH"])
    print ("[Camera Status] - ready")
    return camera

def StopMotionPictureDetection(camera):
    firstFrame = None
    NoMotionCounter = 0
    avg=None
    FrameNumber=conf["FrameNumberToStartFrom"]
    wasemptybefore=False
    while (camera.isOpened()):  # loop over frames from camera
        grabbed, LiveFeed = camera.read()  # read single frame from camera
        if grabbed == True:  # as long as there is a frame,
            Grayscaled_Picture = cv2.cvtColor(LiveFeed, cv2.COLOR_BGR2GRAY)  # convert the LiveFeed to grayscale
            Grayscaled_Picture = cv2.GaussianBlur(Grayscaled_Picture, (21, 21), 0)  # blur the LiveFeed

            if firstFrame is None:  # if the first frame is None, initialize it
                firstFrame = Grayscaled_Picture
                continue

            if avg is None:
                print("[INFO] starting background model...")
                avg = Grayscaled_Picture.copy().astype("float")
                continue

            cv2.accumulateWeighted(Grayscaled_Picture, avg, conf["AccumulatedWeight"]) # accumulate the weighted average between the current frame and previous frames
            frameDelta = cv2.absdiff(Grayscaled_Picture, cv2.convertScaleAbs(avg)) # then compute the difference between the current frame and running average

            thresh = cv2.threshold(frameDelta, conf["ThresholdCalibration"], 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=conf["DilateIterations"])          # dilate the thresholded image to fill in holes, then find contours on thresholded image
            (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)                      # opencv 2.4 requires three arguments to find the contours

            if cnts == []:
                if wasemptybefore == False:
                    FrameNumber = FrameNumber + 1
                    Playsound()
                    cv2.imwrite('C:\Git\openCV\Screenshots\StopMotion' + str(FrameNumber) + '.jpg', LiveFeed)
                    wasemptybefore = True
            else:
                wasemptybefore = False
            ShowVideoOutput(LiveFeed, frameDelta, thresh, firstFrame)
            if cv2.waitKey(1) & 0xFF == 27:  # when ESC button was pressed,
                print("exit")
                CloseCamera(camera)  # call the camera close function
                break
            elif cv2.waitKey(1) & 0xFF == ord("f"):
                LoadConfigFile()
        else:
            CloseCamera(camera)  # call the camera close function
            print("camera not active")
            break  # go back to main menu
    return camera

print ("Main Menu:")                                                                                                      # Main Menu
print ("C - Calibrate Camera")
print ("R - Record Video")
print ("O - Offline Video Analysis")
print ("L - Live Traffic Detection")
print ("M - Make Video")
print ("F - Reload Config File")
print ("Q - Quit")

camera = ""
while True:                                                                                                             # endless loop
    Selection=input("Your Choice : ")
    if Selection.lower() == "c":
        camera = OnlineVideo()
        CameraCalibration(camera)
    if Selection.lower() == "r":
        camera = OnlineVideo()
        RecordVideo(camera)
    if Selection.lower() == "m":
        CreateStopMotionVideo()
    if Selection.lower() == "o":
        camera = OfflineVideo()
        StopMotionPictureDetection(camera)
    if Selection.lower() == "l":
        camera = OnlineVideo()
        StopMotionPictureDetection(camera)
    if Selection.lower() == "f":
        LoadConfigFile()
    if Selection.lower() == "q" or Selection == chr(27):
        if camera != "": CloseCamera(camera)
        print ("quit program")
        break

