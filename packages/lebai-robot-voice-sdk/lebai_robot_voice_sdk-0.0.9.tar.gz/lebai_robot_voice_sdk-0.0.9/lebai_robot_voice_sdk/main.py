from lebai_robot_voice_sdk.base_voice import BaseMiniAudio
from lebai_robot_voice_sdk.errors import LebaiAudioError

class LebaiRobotVoice(BaseMiniAudio):
  def __init__(self) -> None:
    super().__init__()

  # 机器人急停播报
  def play_robot_estop(self):
    try:
      self.play(self.voice_robot_estop_path)
    except Exception as e:
      raise LebaiAudioError(f'机器人急停语音播放失败, 错误信息: {e}')

  # 碗被拿走播报
  def play_bowl_was_token_available(self, index: int):
    try:
      if index < 0 or index > 4:
        raise LebaiAudioError('index 必须在 0 到 4 之间')
      path = self.get_bowl_was_token_available_path(index)
      self.play(path)
    except Exception as e:
      raise LebaiAudioError(f'碗被拿走语音播放失败: {e}')

  # 缺料语音播报
  def play_cabinet_lack_index(self, index: int):
    try:
      if index < 0 or index > 3:
        raise LebaiAudioError('面柜index 必须在 0 到 3 之间')
      path = self.get_out_of_material_path(index)
      self.play(path)
    except Exception as e:
      raise LebaiAudioError(f'缺料语音播报失败: {e}')
  
  # 所有面柜缺料播报
  def play_all_cabinet_lack(self):
    try:
      self.play(self.voice_all_cabinet_lack_path)
    except Exception as e:
      raise LebaiAudioError(f'所有面柜缺料语音播放失败, 错误信息: {e}')


  # 清理料筐
  def play_clean_basket(self):
    try:
      self.play(self.voice_clean_basket_path)
    except Exception as e:
      raise LebaiAudioError(f'清理料筐播放失败, 错误信息: {e}')

  # 汤面请等待加汤
  def play_wait_add_soup(self):
    try:
      self.play(self.voice_wait_add_soup_path)
    except Exception as e:
      raise LebaiAudioError(f'汤面请等待加汤语音播放失败, 错误信息: {e}')

  # 放碗下单时的提醒
  def play_put_bowl_remind(self, index: int):
    try:
      if index < 0 or index > 4:
        raise ValueError('index 必须在 0 到 4 之间')
      path = self.get_put_bowl_remind_path(index)
      self.play(path)
    except Exception as e:
      raise LebaiAudioError(f'放碗下单时的提醒失败: {e}')

  # 制作完成提醒
  def play_turntable_make_complete_remind(self, id: int):
    try:
      if id < 0 or id > 4:
        raise ValueError('参数id 必须在 0 到 4 之间')
      path = self.get_make_complete_remind_path(id)
      self.play(path)
    except Exception as e:
      raise LebaiAudioError(f'制作完成提醒失败: {e}')

  # 播放欢迎语音
  def play_welcome_audio(self):
    try:
      self.play(self.voice_welcome_audio_path)
    except Exception as e:
      raise LebaiAudioError(f'欢迎语音播放失败: {e}')


if __name__ == '__main__':
  try:
    lebai_turntable_voice = LebaiRobotVoice()
    lebai_turntable_voice.play_welcome_audio()
  except LebaiAudioError as e:
    print(f'LebaiAudioError 错误: {e}')
  except Exception as e:
    print(f'报错: {e}')
  