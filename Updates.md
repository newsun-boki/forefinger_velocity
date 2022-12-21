# 12.21更新
在`data2sound.py`中添加socket服务端接收信息来改变音频大小volume
+ 在data2sound这个进程使用新的线程`getVolume`,来改变全局变量volume的值
+ 可以使用`socketClientTest.py`来测试socket的发送是否正常