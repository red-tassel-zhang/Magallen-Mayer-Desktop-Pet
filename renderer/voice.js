// 语音播放系统 - 使用 .wav 音频文件

const VoiceSystem = {
  currentAudio: null,
  speaking: false,
  onEndCallback: null,

  // 播放语音文件
  play(filePath, onEnd) {
    if (!filePath) return;

    // 停止当前播放
    this.stop();

    const audio = new Audio(filePath);
    audio.volume = 0.9;

    audio.onplay = () => {
      this.speaking = true;
    };

    audio.onended = () => {
      this.speaking = false;
      this.currentAudio = null;
      if (onEnd) onEnd();
      if (this.onEndCallback) {
        const cb = this.onEndCallback;
        this.onEndCallback = null;
        cb();
      }
    };

    audio.onerror = (e) => {
      console.error('Audio playback error:', e);
      this.speaking = false;
      this.currentAudio = null;
      if (onEnd) onEnd();
      if (this.onEndCallback) {
        const cb = this.onEndCallback;
        this.onEndCallback = null;
        cb();
      }
    };

    this.currentAudio = audio;
    audio.play().catch(err => {
      console.error('Audio play() rejected:', err);
      this.speaking = false;
      this.currentAudio = null;
    });
  },

  // 带气泡文字的播放
  speak(filePath, onEnd) {
    const text = getVoiceText(filePath);
    if (text && window.showBubble) {
      const duration = Math.max(2500, text.length * 100);
      window.showBubble(text, duration);
    }
    this.play(filePath, onEnd);
  },

  stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    this.speaking = false;
  },

  isSpeaking() {
    return this.speaking;
  },
};
