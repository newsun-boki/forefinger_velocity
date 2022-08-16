# 手部速度估计

通过mediapipe识别手，显示食指移动速度，可视化并将其转换为音频信号。

## I.环境

+ numpy
+ cvzone
+ mediapipe
+ python-opencv
+ pyqt5 & pyqtgraph
+ pyaudio


## II.介绍

项目整体采用多进程的结构(mutiprocessing)，运行[mutiProcessMain.py](mutiProcessMain.py)脚本可以运行所有的进程，各个进程之间通过队列进行通信。四个进程分别为：

+ 主进程[(mutiProcessMain.py)](mutiProcessMain.py)：包含手部识别，食指位置识别，相机坐标转换。帧率30HZ左右
+ 子进程1[(observer.py)](./process/observer.py)：包含速度解算，滤波，预测。以3000HZ实时估计当前速度。
+ 子进程2[(pyqt5graph.py)](./process/pyqt5graph.py)：通过qt实时绘制当前速度曲线，帧率为20HZ。
+ 子进程3[(data2sound.py)](./process/data2sound.py)：将当前食指速度转化为音频，速度与音频的频率正相关。帧率1000HZ。

注意：由于子进程2和子进程3会互相冲突，默认开启子进程2。可通过在[mutiProcessMain.py](mutiProcessMain.py)中129行注释`plot.start()`关闭子进程2。并在130行取消注释`audio.start()`开启子进程3。

经测试，子进程2和子进程3有几率造成整体程序短暂卡顿。

## III.快速开始
 ```python
 pip install -r requirements.txt
 python mutiProcessMain.py
 ```

## IV.参数说明

+ 相机内参：用于将手部速度转化到相机坐标系中，包括内参矩阵(camera_matrix)以及畸变参数(distCoeffs),于[mutiProcessMain.py](mutiProcessMain.py)中105行至111行处修改。可使用[calibrator.py](calibrator.py)或matlab对相机进行标定
+ z_cam: 由于难以获取深度信息，固定相机与手指距离，默认470mm.于[mutiProcessMain.py](mutiProcessMain.py)中104行
+ 其他参数详见代码
  
## V.可视化
通过opencv实时显示识别手以及食指的轨迹，其中的点是采样点，点的颜色代表手移动的速度。越偏蓝的点速度越慢，反之越红的点速度越快。

![](https://media.giphy.com/media/0DixGSD54VXMcVM71w/giphy.gif)

使用matplotlib实时显示食指运动轨迹，同样线的颜色会随着手的速度变化。
  
![](https://media.giphy.com/media/5fbrq8LncPV2dYy0VR/giphy.gif)

使用qt绘制出手部数据的实时曲线

![](https://media.giphy.com/media/gvnhA8defsQp7BeJSi/giphy-downsized-large.gif)

### VI.多线程
一开始尝试的是使用多线程，但python多线程并不能完整的利用CPU内存资源，会造成主进程卡顿，但多线程下数据交互方便可作为可作可视化预测验证。
