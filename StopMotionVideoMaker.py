from imutils.video import VideoStream
import time
import cv2
import os
import numpy
import datetime
import argparse
import json
import vlc

# Define project-relative paths
root_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(root_dir, "StopMotion.json")
videos_dir = os.path.join(root_dir, "Videos")
screenshots_dir = os.path.join(root_dir, "Screenshots")
sounds_dir = os.path.join(root_dir, "Sounds")

# Load config
conf = json.load(open(config_path))

def LoadConfigFile():
    global conf
    conf = json.load(open(config_path))
    print("Config File Reloaded")
    return conf

def Playsound():
    if conf["PlaySound"]:
        sound_path = os.path.join(sounds_dir, "CameraClick.mp3")
        p = vlc.MediaPlayer(sound_path)
        p.play()
    else:
        print("Sound not activated - picture taken")

def ShowVideoOutput(LiveFeed, frameDelta, thresh, firstFrame):
    if conf["ShowPictures"]:
        cv2.imshow("Live View", LiveFeed)
        cv2.imshow("Frame Delta", frameDelta)
        cv2.imshow("Thresholded View", thresh)
        cv2.imshow("Background substraction base", firstFrame)

def CloseCamera(camera):
    cv2.destroyAllWindows()
    print("[Camera Status] - deactivated")
    camera.release()

def RecordVideo(camera):
    VideoName = input("VideoName (without extension): ")
    video_path = os.path.join(videos_dir, f"{VideoName}.avi")

    if os.path.isfile(video_path):
        Selection = input("File exists! Overwrite? (y/n): ")
        if Selection.lower() == "y":
            os.remove(video_path)
        else:
            return RecordVideo(camera)

    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    RecordedVideo = cv2.VideoWriter(video_path, fourcc, 25, (640, 480), True)

    while True:
        grabbed, LiveFeed = camera.read()
        if grabbed:
            RecordedVideo.write(LiveFeed)
            cv2.putText(LiveFeed, f"Recording file .. {video_path}",
                        (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 0, 255), 2)
            cv2.imshow('Recorder', LiveFeed)
            if cv2.waitKey(1) & 0xFF == 27:
                CloseCamera(camera)
                RecordedVideo.release()
                break
        else:
            CloseCamera(camera)
            RecordedVideo.release()
            break
    return camera

def CreateStopMotionVideo():
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    video_path = os.path.join(videos_dir, "StopMotion.avi")
    video = cv2.VideoWriter(video_path, fourcc, 1, (conf["ResolutionW"], conf["ResolutionH"]), True)

    for j in range(1, 9):
        image_path = os.path.join(screenshots_dir, f"StopMotion{j}.jpg")
        img = cv2.imread(image_path)
        print(f"Reading {image_path}")
        cv2.imshow('Recorder', img)
        time.sleep(1)
        video.write(img)

    cv2.destroyAllWindows()
    video.release()

def CameraCalibration(camera):
    while camera.isOpened():
        grabbed, LiveFeed = camera.read()
        if grabbed:
            cv2.imshow('Calibration Window - press ESC to finalize', LiveFeed)
            if cv2.waitKey(1) & 0xFF == 27:
                print("Calibration finished")
                CloseCamera(camera)
                break
            elif cv2.waitKey(1) & 0xFF == ord("f"):
                LoadConfigFile()
        else:
            CloseCamera(camera)
            print("Camera not active")
            break
    return camera

def OfflineVideo():
    print("All *.avi files in", videos_dir, ":")
    for file in os.listdir(videos_dir):
        if file.endswith(".avi"):
            print(file)

    Selection = input("Select file to play (without extension): ")
    video_path = os.path.join(videos_dir, Selection + ".avi") if Selection else os.path.join(videos_dir, "Video_oneobj_2.avi")

    if not os.path.isfile(video_path):
        print("File not found!")
        return OfflineVideo()

    print("Selected file:", video_path)
    camera = cv2.VideoCapture(video_path)
    return camera

def OnlineVideo():
    print("[Camera Status] - warming up")
    time.sleep(1.0)
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, conf["ResolutionW"])
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, conf["ResolutionH"])
    print("[Camera Status] - ready")
    return camera

def StopMotionPictureDetection(camera):
    firstFrame = None
    avg = None
    wasemptybefore = False
    FrameNumber = conf["FrameNumberToStartFrom"]

    while camera.isOpened():
        grabbed, LiveFeed = camera.read()
        if grabbed:
            gray = cv2.cvtColor(LiveFeed, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if firstFrame is None:
                firstFrame = gray
                continue

            if avg is None:
                print("[INFO] Starting background model...")
                avg = gray.copy().astype("float")
                continue

            cv2.accumulateWeighted(gray, avg, conf["AccumulatedWeight"])
            frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

            thresh = cv2.threshold(frameDelta, conf["ThresholdCalibration"], 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=conf["DilateIterations"])
            (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not cnts and not wasemptybefore:
                FrameNumber += 1
                Playsound()
                screenshot_path = os.path.join(screenshots_dir, f"StopMotion{FrameNumber}.jpg")
                cv2.imwrite(screenshot_path, LiveFeed)
                wasemptybefore = True
            elif cnts:
                wasemptybefore = False

            ShowVideoOutput(LiveFeed, frameDelta, thresh, firstFrame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                print("Exit")
                CloseCamera(camera)
                break
            elif key == ord("f"):
                LoadConfigFile()
        else:
            CloseCamera(camera)
            print("Camera not active")
            break
    return camera

# ------------------- MAIN MENU --------------------
print("Main Menu:")
print("C - Calibrate Camera")
print("R - Record Video")
print("O - Offline Video Analysis")
print("L - Live Traffic Detection")
print("M - Make Video")
print("F - Reload Config File")
print("Q - Quit")

camera = ""
while True:
    Selection = input("Your Choice: ")
    if Selection.lower() == "c":
        camera = OnlineVideo()
        CameraCalibration(camera)
    elif Selection.lower() == "r":
        camera = OnlineVideo()
        RecordVideo(camera)
    elif Selection.lower() == "m":
        CreateStopMotionVideo()
    elif Selection.lower() == "o":
        camera = OfflineVideo()
        StopMotionPictureDetection(camera)
    elif Selection.lower() == "l":
        camera = OnlineVideo()
        StopMotionPictureDetection(camera)
    elif Selection.lower() == "f":
        LoadConfigFile()
    elif Selection.lower() == "q" or Selection == chr(27):
        if camera:
            CloseCamera(camera)
        print("Quit program")
        break
