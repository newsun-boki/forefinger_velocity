# Hand Speed Estimator

Recognize hand through mediapipe, display index finger movement speed, visualize and convert it into audio signal.

## I.Environments

+ numpy
+ cvzone
+ mediapipe
+ python-opencv
+ pyqt5 & pyqtgraph
+ pyaudio


## II. Introduction

The project as a whole adopts a multi-process structure (mutiprocessing). Running the [mutiProcessMain.py](mutiProcessMain.py) script can run all processes, and each process communicates through queues. The four processes are:

+ Main process [(mutiProcessMain.py)](mutiProcessMain.py): including hand recognition, index finger position recognition, and camera coordinate conversion. Frame rate around 30HZ
+ Subprocess 1[(observer.py)](./process/observer.py): Contains velocity calculation, filtering, and prediction. Estimate current speed in real time at 3000HZ.
+ Subprocess 2[(pyqt5graph.py)](./process/pyqt5graph.py): draw the current speed curve in real time through qt, and the frame rate is 20HZ.
+ Subprocess 3[(data2sound.py)](./process/data2sound.py): Convert the current index finger speed into audio, and the speed is positively related to the frequency of the audio. Frame rate 1000HZ.

Note: Since child process 2 and child process 3 will conflict with each other, child process 2 is enabled by default. Subprocess 2 can be shut down by commenting out `plot.start()` on line 129 in [mutiProcessMain.py](mutiProcessMain.py). And uncomment `audio.start()` on line 130 to start child process 3.

After testing, sub-process 2 and sub-process 3 have a chance to cause the overall program to freeze temporarily.

## III. Quick Start
 ````python
 pip install -r requirements.txt
 python mutiProcessMain.py
 ````

## IV. Parameter description

+ Camera internal parameters: used to convert the hand speed into the camera coordinate system, including the internal parameter matrix (camera_matrix) and distortion parameters (distCoeffs), modified in [mutiProcessMain.py] (mutiProcessMain.py) line 105 to line 111. The camera can be calibrated using [calibrator.py](calibrator.py) or matlab
+ z_cam: Since it is difficult to obtain depth information, the distance between the camera and the finger is fixed, the default is 470mm. In [mutiProcessMain.py](mutiProcessMain.py), line 104
+ See the code for other parameters