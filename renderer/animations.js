// 动画状态机

const AnimationState = {
  current: 'idle',
  previous: null,
  transitionTime: 0,
  stateStartTime: 0,

  // 状态配置
  states: {
    idle: {
      loop: true,
      duration: Infinity,
      onEnter() {
        PetDrawer.bodyBob = 0;
        PetDrawer.armWave = 0;
        PetDrawer.eyeOpen = true;
        PetDrawer.mouthOpen = false;
        PetDrawer.droneVisible = false;
        PetDrawer.sleepy = false;
        PetDrawer.blushLevel = 0;
        PetDrawer.tearDrop = false;
      },
      update(t) {
        // 呼吸效果已通过 pet.draw 中的 sin 实现
      },
    },
    blink: {
      loop: false,
      duration: 150,
      onEnter() {
        PetDrawer.eyeOpen = false;
      },
      onExit() {
        PetDrawer.eyeOpen = true;
      },
    },
    clicked: {
      loop: false,
      duration: 600,
      onEnter() {
        PetDrawer.armWave = 0.8;
        PetDrawer.mouthOpen = true;
        PetDrawer.blushLevel = 1;
      },
      update(t, progress) {
        PetDrawer.bodyBob = Math.sin(progress * Math.PI * 3) * 8 * (1 - progress);
        PetDrawer.armWave = 0.8 * (1 - progress);
      },
      onExit() {
        PetDrawer.armWave = 0;
        PetDrawer.mouthOpen = false;
        PetDrawer.blushLevel = 0;
        PetDrawer.bodyBob = 0;
      },
    },
    walk: {
      loop: true,
      duration: Infinity,
      onEnter() {
        PetDrawer.droneVisible = false;
        PetDrawer.mouthOpen = false;
      },
      update(t) {
        PetDrawer.bodyBob = Math.abs(Math.sin(t * 0.008)) * 6;
        PetDrawer.armWave = Math.sin(t * 0.008) * 0.6;
      },
      onExit() {
        PetDrawer.bodyBob = 0;
        PetDrawer.armWave = 0;
      },
    },
    talking: {
      loop: false,
      duration: 3000,
      onEnter() {},
      update(t) {
        // 模拟说话嘴部张合
        PetDrawer.mouthOpen = Math.sin(t * 0.02) > 0;
      },
      onExit() {
        PetDrawer.mouthOpen = false;
      },
    },
    drone: {
      loop: false,
      duration: 3500,
      onEnter() {
        PetDrawer.droneVisible = true;
        PetDrawer.armWave = 0.6;
      },
      update(t, progress) {
        PetDrawer.armWave = 0.6 * (1 - progress);
        if (progress > 0.2) {
          PetDrawer.mouthOpen = Math.sin(t * 0.015) > 0;
        }
      },
      onExit() {
        PetDrawer.droneVisible = false;
        PetDrawer.armWave = 0;
        PetDrawer.mouthOpen = false;
      },
    },
    sleepy: {
      loop: false,
      duration: 6000,
      onEnter() {
        PetDrawer.sleepy = true;
        PetDrawer.mouthOpen = true;
      },
      update(t) {
        PetDrawer.bodyBob = Math.sin(t * 0.002) * 3;
      },
      onExit() {
        PetDrawer.sleepy = false;
        PetDrawer.mouthOpen = false;
        PetDrawer.bodyBob = 0;
      },
    },
    happy: {
      loop: false,
      duration: 2000,
      onEnter() {
        PetDrawer.blushLevel = 1;
        PetDrawer.bodyBob = 0;
      },
      update(t, progress) {
        PetDrawer.bodyBob = Math.abs(Math.sin(progress * Math.PI * 4)) * 12 * (1 - progress);
        PetDrawer.armWave = Math.sin(progress * Math.PI * 4) * (1 - progress);
        PetDrawer.mouthOpen = Math.sin(t * 0.03) > 0;
      },
      onExit() {
        PetDrawer.blushLevel = 0;
        PetDrawer.bodyBob = 0;
        PetDrawer.armWave = 0;
        PetDrawer.mouthOpen = false;
      },
    },
  },

  setState(stateName, duration) {
    const prevState = this.states[this.current];
    if (prevState && prevState.onExit) {
      prevState.onExit();
    }

    this.previous = this.current;
    this.current = stateName;
    this.stateStartTime = performance.now();

    const state = this.states[stateName];
    if (state && state.onEnter) {
      state.onEnter();
    }

    // 如果传了自定义 duration，覆盖默认
    if (duration && state) {
      state.duration = duration;
    }
  },

  getElapsed() {
    return performance.now() - this.stateStartTime;
  },

  getProgress() {
    const state = this.states[this.current];
    const elapsed = this.getElapsed();
    return Math.min(elapsed / state.duration, 1);
  },

  update(timestamp) {
    const state = this.states[this.current];
    if (!state) return;

    const elapsed = timestamp - this.stateStartTime;
    const progress = Math.min(elapsed / state.duration, 1);

    if (state.update) {
      state.update(timestamp, progress);
    }

    // 非循环状态结束后回到 idle
    if (!state.loop && elapsed >= state.duration) {
      this.setState('idle');
    }
  },

  // 随机眨眼
  lastBlink: 0,
  nextBlinkInterval: 0,

  checkBlink(timestamp) {
    if (this.current === 'idle' || this.current === 'walk') {
      if (!this.nextBlinkInterval) {
        this.nextBlinkInterval = 2000 + Math.random() * 4000;
      }
      if (timestamp - this.lastBlink > this.nextBlinkInterval) {
        this.lastBlink = timestamp;
        this.nextBlinkInterval = 2000 + Math.random() * 4000;
        // 插入眨眼（不影响当前 idle 状态）
        PetDrawer.eyeOpen = false;
        setTimeout(() => {
          if (this.current === 'idle' || this.current === 'walk') {
            PetDrawer.eyeOpen = true;
          }
        }, 120);
      }
    }
  },
};
