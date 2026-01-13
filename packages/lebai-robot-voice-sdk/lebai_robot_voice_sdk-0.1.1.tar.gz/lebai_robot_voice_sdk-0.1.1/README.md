乐白机器人语音播报Python SDK。除了语音播放相关的方法可以使用（播放，停止播放，设置音量）。还封装了转盘煮面业务语音，方便调用

# 安装
```powershell
lpy -m pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple lebai_robot_voice_sdk 
```

```powershell
pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple lebai_robot_voice_sdk
```

## 更新 pip 包
```powershell
lpy -m pip install --upgrade -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple lebai_robot_voice_sdk
```

# 快速上手
`lebai_robot_voice_sdk` 使用起来非常简单，安装完软件包后，python 程序里我们直接引入， 初始化实例，就可以使用了，下面是示例:

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

# 初始化实例
voice = LebaiRobotVoice()

try:
    # 播放任意语音文件,audio_path是你任意语音文件的文件路径
    voice.play(audio_path)  
    
    # 转盘欢迎语音播报
    voice.play_welcome_audio()  

    # 播放机器人急停播报
    voice.play_robot_estop()  

    # 播放碗被拿走播报（index: 0-4）
    voice.play_bowl_was_token_available(0)  

    # 播放缺料语音播报（index: 0-3）
    voice.play_cabinet_lack_index(0)  

    # 播放所有面柜缺料播报
    voice.play_all_cabinet_lack()  

    # 清理料筐播报
    voice.play_clean_basket()  

    # 汤面请等待加汤播报
    voice.play_wait_add_soup()  

    # 放碗下单时的提醒（index: 0-4）
    voice.play_put_bowl_remind(0)  

    # 制作完成提醒（id: 0-4）
    voice.play_turntable_make_complete_remind(0)  

except LebaiAudioError as e:  
    print(f"语音播报错误: {e}")
```

# 特性说明

## 串行执行原则
语音播报遵循串行执行原则，举个例子：

```python
voice.play(path)
print("播放完了")
```

举例：假设有两行代码，只有等语音完全播放完毕， 比如这个语音文件时长为 5 秒，那么只有等语音完全播放完毕， 5 秒后才会执行下面的打印。依据此特性我们可以做任意逻辑，比如播报完后我们 `time.sleep(3)`延迟 3 秒继续播其他语音，或者循环的进行播放。

# 方法
实例化后`voice = LebaiRobotVoice()`，我们就可以调用不同的方法了，下面的都以 voice 为例。

## play
播放任意语音文件（最好 mp3 格式）。

参数:

+ path: 需要传入任意并存在的音频文件路径。

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError  # pyright: ignore[reportMissingImports]
import pathlib

voice_path = pathlib.Path(__file__).parent / "assets" / "test.mp3"


if __name__ == "__main__":
  try:
    voice = LebaiRobotVoice()
    voice.play(voice_path)
  except LebaiAudioError as e:
    print(f"Error: {e}")
    exit(1)

```

## set_volume
设置语音音量。

参数:

+ volume: 需要传入0-100之间的整数。

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.set_volume(50)
except LebaiAudioError as e:
    print(f"Error: {e}")
    exit(1)
```

## get_audio_duration
获取语音文件时长

| | 值 | 类型 |
| --- | --- | --- |
| 参数 | path: 需要传入任意并存在的音频文件路径。 | |
| 返回值 | duration 秒 | float 浮点型 |


```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.get_audio_duration(path)
except LebaiAudioError as e:
    print(f"Error: {e}")
    exit(1)
```

## stop
停止语音播放。

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.stop()
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## close_audio_device
关闭音频设备，这个不常用，一般调度关闭的时候需要关掉

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.close_audio_device()
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_robot_estop
机器人急停语音播报

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_robot_estop()  
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_bowl_was_token_available
碗被拿走播报

| | 值 | 类型 |
| --- | --- | --- |
| 参数 | index 0~4 代表第几个碗位 | int |
| 返回值 |  |  |


```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()

    voice.play_bowl_was_token_available(0)     
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_cabinet_lack_index
缺料语音播报，只播报某一层

| | 值 | 类型 |
| --- | --- | --- |
| 参数 | index 0~3 代表第几层面柜 | int |
| 返回值 |  |  |


```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_cabinet_lack_index(0)       
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_all_cabinet_lack
所有面柜缺料播报

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_all_cabinet_lack()         
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_clean_basket
清理料盒框播报

```python

from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_clean_basket() 
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_wait_add_soup
汤面请等待加汤播报

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_wait_add_soup()             
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_put_bowl_remind
放碗下单时的提醒语音

| | 值 | 类型 |
| --- | --- | --- |
| 参数 | index 0~4 代表第几个碗位下单 | int |
| 返回值 |  |  |


```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_put_bowl_remind(0)               
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_turntable_make_complete_remind
制作完成提醒

| | 值 | 类型 |
| --- | --- | --- |
| 参数 | index 0~4 代表第几个碗位制作完成 | int |
| 返回值 |  |  |


```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_turntable_make_complete_remind(0)                 
except LebaiAudioError as e:
    print(f"Error: {e}")
```

## play_welcome_audio
转盘煮面欢迎语音播报

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    voice.play_turntable_loop_audio()                   
except LebaiAudioError as e:
    print(f"Error: {e}")
```

# 属性
## playing
获取当前是否正在语音播报

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError

try:
    voice = LebaiRobotVoice()
    print(voice.playing)
except LebaiAudioError as e:  
    print(f"Error: {e}")
```

# 异常处理
我们通过 try except 捕获LebaiAudioError，就能捕获到有关该软件包的异常错误，方便打日志。

```python
from lebai_robot_voice_sdk import LebaiRobotVoice, LebaiAudioError  

try:
    voice = LebaiRobotVoice()
    ...
except LebaiAudioError as e: 
    logger.error(e)
    print(f"lebai_robot_voice_sdk相关错误: {e}")
```

