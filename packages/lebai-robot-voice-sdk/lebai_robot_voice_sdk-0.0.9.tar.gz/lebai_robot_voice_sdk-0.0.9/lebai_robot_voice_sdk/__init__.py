"""
Lebai Robot Voice SDK

一个用于乐白机器人语音播报的Python SDK。
"""

from lebai_robot_voice_sdk.main import LebaiRobotVoice
from lebai_robot_voice_sdk.errors import LebaiAudioError

__version__ = "0.0.9"
__all__ = ['LebaiRobotVoice', 'LebaiAudioError']
