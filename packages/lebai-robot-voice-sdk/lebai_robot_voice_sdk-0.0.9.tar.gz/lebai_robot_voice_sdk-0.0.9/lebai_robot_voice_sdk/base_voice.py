import miniaudio  # pyright: ignore[reportMissingImports]
import time
from pathlib import Path
import subprocess
import platform
from lebai_robot_voice_sdk.errors import LebaiAudioError


class BaseMiniAudio:
  def __init__(self) -> None:
    self.is_playing_audio = False
    self.init_audio_device()
    self.setup_audio()

    # 基础路径，便于统一修改
    self.base_path = Path(__file__).parent

    self.voice_welcome_audio_path = self.base_path / 'assets' / 'mp3' / '欢迎语音.mp3'
    self.voice_robot_estop_path = self.base_path / 'assets' / 'mp3' / '机械臂急停.mp3'
    # 所有面柜缺料
    self.voice_all_cabinet_lack_path = self.base_path / 'assets' / 'mp3' / 'cabinet_lack' / '面柜已空.mp3'
    # 清理料筐
    self.voice_clean_basket_path = self.base_path / 'assets' / 'mp3' / '请清理料盒筐.mp3'
    # 汤面请等待加汤
    self.voice_wait_add_soup_path = self.base_path / 'assets' / 'mp3' / '汤面请等待加汤.mp3'


  @property
  def playing(self):
    return self.is_playing_audio

  @property
  def play_back_device(self):
    return self.audio_device


  # 后台程序
  def setup_audio(self):
    """设置音频参数"""
    current_system = platform.system()
    if current_system != 'Darwin':
      try:
        subprocess.run(['amixer', 'set', 'Playback Path', 'HP'], 
                      capture_output=True, timeout=5)
        subprocess.run(['amixer', 'set', 'Playback', '100%'],
                      capture_output=True, timeout=5)
      except Exception as e:
        raise LebaiAudioError(f'音频后台程序执行报错, 当前操作系统: {current_system}, 错误信息: {e}')



  def init_audio_device(self) -> None:
    try:
      self.audio_device = miniaudio.PlaybackDevice()
    except OSError as e:
      raise LebaiAudioError(f'提示: 请检查系统是否安装了音频驱动和音频设备: {e}')
    except Exception as e:
      raise LebaiAudioError(f'音频设备未知错误: {e}')


  # 设置音频音量 0~100
  def set_volume(self, volume: int):
    if volume < 0 or volume > 100:
      raise LebaiAudioError('音量必须在 0 到 100 之间')
    try:
      subprocess.run(['amixer', 'set', 'Playback', f'{volume}%'],
                      capture_output=True, timeout=5)
    except Exception as e:
      raise LebaiAudioError(f'设置音频音量失败: {e}')


  def play(self, file_path):
    if self.is_playing_audio:
      return
    try:
      self.is_playing_audio = True
      stream = miniaudio.stream_file(file_path)
      duration = self.get_audio_duration(file_path)
      self.audio_device.start(stream)
      time.sleep(duration)
      self.stop()
    except Exception as e:
      self.is_playing_audio = False
      raise LebaiAudioError(f'播放音频失败, 错误信息: {e}')

  # 随时停止语音播报, 可以停止流
  def stop(self):
    self.audio_device.stop()
    self.is_playing_audio = False

  # 获取音频文件时长
  def get_audio_duration(self, file_path):
    try:
      audio_file_info = miniaudio.get_file_info(file_path)
      return audio_file_info.duration
    except Exception as e:
      raise LebaiAudioError(f'获取音频文件时长失败: {e}')

  # 关闭音频设备
  def close_audio_device(self):
    self.audio_device.close()
    self.is_playing_audio = False


  



  






  def get_bowl_was_token_available_path(self, index: int):
    return self.base_path / 'assets' / 'mp3' / 'bowl_was_tokenaway' / f'{index + 1}号位碗被拿走.mp3'

  # 单个缺料语音播报
  def get_out_of_material_path(self, index: int):
    return self.base_path / 'assets' / 'mp3' / 'cabinet_lack' / f'面柜{index + 1}层缺料.mp3'
  
  # 放碗下单时的提醒
  def get_put_bowl_remind_path(self, index: int):
    return self.base_path / 'assets' / 'mp3' / 'order' / f'{index + 1}号下单.mp3'

  # 制作完成提醒
  def get_make_complete_remind_path(self, id: int):
    return self.base_path / 'assets' / 'mp3' / 'order' / f'{id + 1}号下单.mp3'
