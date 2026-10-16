"""语音播放 —— 使用 QMediaPlayer 播放 WAV

早期版本用的 QSoundEffect 有个问题：setSource 是异步加载，
连续快速切换文件时（第3次开始）内部状态会失锁导致静音。
QMediaPlayer 内部有队列/状态机保护，切换 source 更稳定。
"""
import os
import threading

try:
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtCore import QUrl
    HAS_QT_AUDIO = True
except ImportError:
    HAS_QT_AUDIO = False


class VoicePlayer:
    def __init__(self):
        self._player = None
        self._audio = None
        self._on_end = None
        self.playing = False
        self.muted = False
        if HAS_QT_AUDIO:
            self._audio = QAudioOutput()
            self._audio.setVolume(0.9)
            self._player = QMediaPlayer()
            self._player.setAudioOutput(self._audio)
            self._player.playbackStateChanged.connect(self._on_state_changed)

    def play(self, path, on_end=None):
        if not path or not os.path.exists(path):
            if on_end:
                on_end()
            return
        if self.muted:
            if on_end:
                on_end()
            return
        self._on_end = on_end
        if HAS_QT_AUDIO:
            self._play_qt(path)
        else:
            self._play_winsound_threaded(path)

    def _play_qt(self, path):
        # QMediaPlayer 允许直接换 source，Qt 内部会正确处理
        self._player.stop()
        self._player.setSource(QUrl.fromLocalFile(path))
        self._player.play()
        self.playing = True

    def _on_state_changed(self, state):
        # StoppedState=0, PlayingState=1, PausedState=2
        if state == QMediaPlayer.StoppedState and self.playing:
            self.playing = False
            if self._on_end:
                cb = self._on_end
                self._on_end = None
                cb()

    def _play_winsound_threaded(self, path):
        import winsound

        def _run():
            self.playing = True
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME)
            except Exception:
                pass
            self.playing = False
            if self._on_end:
                cb = self._on_end
                self._on_end = None
                cb()

        t = threading.Thread(target=_run, daemon=True)
        t.start()

    def stop(self):
        if HAS_QT_AUDIO and self._player:
            self._player.stop()
        self.playing = False
