// 交互系统 - 点击、拖拽、自主行为、闲置层级、右键菜单

const Interactions = {
  canvas: null,
  bubble: null,
  bubbleText: null,
  contextMenu: null,

  // 拖拽
  isDragging: false,
  dragStartX: 0,
  dragStartY: 0,
  dragThreshold: 5,
  hasMoved: false,

  // 点击
  lastClickTime: 0,
  clickTimer: null,

  // 闲置计时器
  fidgetTimer: null,     // 小动作
  autoWalkTimer: null,   // 自主走动
  sitTimer: null,        // 坐下
  chatTimer: null,       // 闲聊
  sleepTimer: null,      // 睡觉

  // 走动
  walkTimer: null,
  walkStopTimer: null,
  walkDir: 1,

  // 气泡
  bubbleHideTimer: null,

  // 记录窗口大致位置（用于屏幕边界检测）
  windowX: 0,
  windowY: 0,

  init() {
    this.canvas = document.getElementById('pet-canvas');
    this.bubble = document.getElementById('speech-bubble');
    this.bubbleText = document.getElementById('bubble-text');
    this.contextMenu = document.getElementById('context-menu');

    this.bindEvents();
    this.refreshWindowBounds();
    this.startIdleBehaviors();
  },

  bindEvents() {
    this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
    document.addEventListener('mousemove', (e) => this.onMouseMove(e));
    document.addEventListener('mouseup', (e) => this.onMouseUp(e));
    document.addEventListener('mouseleave', () => this.onMouseUp({}));

    this.canvas.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      this.showContextMenu(e);
    });

    this.contextMenu.querySelectorAll('.menu-item').forEach(item => {
      item.addEventListener('click', (e) => {
        this.handleMenuAction(item.dataset.action);
        this.hideContextMenu();
      });
    });

    document.addEventListener('click', (e) => {
      if (!this.contextMenu.contains(e.target)) this.hideContextMenu();
    });
  },

  // === 获取窗口屏幕位置 ===
  async refreshWindowBounds() {
    if (window.electronAPI && window.electronAPI.getWindowBounds) {
      try {
        const b = await window.electronAPI.getWindowBounds();
        if (b) {
          this.windowX = b.x;
          this.windowY = b.y;
          this.screenW = b.screenWidth;
          this.screenH = b.screenHeight;
          this.winW = b.width;
          this.winH = b.height;
        }
      } catch (_) {}
    }
  },

  // === 鼠标事件 ===
  onMouseDown(e) {
    this.isDragging = true;
    this.hasMoved = false;
    this.dragStartX = e.screenX;
    this.dragStartY = e.screenY;
    this.hideContextMenu();
  },

  onMouseMove(e) {
    if (!this.isDragging) return;
    const dx = e.screenX - this.dragStartX;
    const dy = e.screenY - this.dragStartY;

    if (Math.abs(dx) > this.dragThreshold || Math.abs(dy) > this.dragThreshold) {
      this.hasMoved = true;
    }

    if (this.hasMoved && window.electronAPI) {
      window.electronAPI.moveWindow(dx, dy);
      this.windowX += dx;
      this.windowY += dy;
      this.dragStartX = e.screenX;
      this.dragStartY = e.screenY;
    }
  },

  onMouseUp(e) {
    if (!this.isDragging) return;
    this.isDragging = false;

    if (!this.hasMoved) {
      const now = Date.now();
      if (now - this.lastClickTime < 350) {
        this.handleDoubleClick();
        this.lastClickTime = 0;
        if (this.clickTimer) clearTimeout(this.clickTimer);
      } else {
        this.lastClickTime = now;
        if (this.clickTimer) clearTimeout(this.clickTimer);
        this.clickTimer = setTimeout(() => {
          this.handleClick();
          this.lastClickTime = 0;
        }, 360);
      }
    }
    this.refreshWindowBounds();
    this.resetIdleBehaviors();
  },

  // === 点击/双击 ===
  handleClick() {
    PetPlayer.play('interact', () => PetPlayer.play('relax'));
    const v = getRandomVoice('click');
    if (v) VoiceSystem.speak(v);
  },

  handleDoubleClick() {
    PetPlayer.play('skill', () => PetPlayer.play('relax'));
    const v = getRandomVoice('doubleClick');
    if (v) VoiceSystem.speak(v);
  },

  // === 右键菜单 ===
  handleMenuAction(action) {
    this.resetIdleBehaviors();
    switch (action) {
      case 'talk': {
        PetPlayer.play('interact', () => PetPlayer.play('relax'));
        const v = getRandomVoice('menuTalk');
        if (v) VoiceSystem.speak(v);
        break;
      }
      case 'skill': {
        PetPlayer.play('skill', () => PetPlayer.play('relax'));
        const v = getRandomVoice('menuSkill');
        if (v) VoiceSystem.speak(v);
        break;
      }
      case 'walk': {
        this.startAutonomousWalk(8);
        const v = getRandomVoice('menuWalk');
        if (v) VoiceSystem.speak(v);
        break;
      }
      case 'sit': {
        this.stopWalk();
        PetPlayer.play('sit');
        const v = getRandomVoice('menuSit');
        if (v) VoiceSystem.speak(v);
        break;
      }
      case 'sleep': {
        this.stopWalk();
        PetPlayer.play('sleep');
        const v = getRandomVoice('menuSleep');
        if (v) VoiceSystem.speak(v);
        break;
      }
      case 'hide':
        if (window.electronAPI) window.electronAPI.minimizeApp();
        break;
      case 'quit':
        PetPlayer.play('die', () => {
          setTimeout(() => {
            if (window.electronAPI) window.electronAPI.closeApp();
          }, 300);
        });
        break;
    }
  },

  // === 闲置行为层级 ===
  startIdleBehaviors() {
    this.scheduleFidget();
    this.scheduleAutoWalk();
    this.scheduleSit();
    this.scheduleChat();
    this.scheduleSleep();
  },

  resetIdleBehaviors() {
    // 清除所有计时器
    [this.fidgetTimer, this.autoWalkTimer, this.sitTimer,
     this.chatTimer, this.sleepTimer].forEach(t => {
      if (t) clearTimeout(t);
    });

    // 从睡眠/坐下醒来
    const cur = PetPlayer.activeAnim;
    if (cur === 'sleep' || cur === 'sit') {
      PetPlayer.play('relax');
    }
    this.stopWalk();

    // 重新调度
    this.startIdleBehaviors();
  },

  // 小动作：每 15-35 秒，快速 interact 动画（不说话）
  scheduleFidget() {
    const delay = 15000 + Math.random() * 20000;
    this.fidgetTimer = setTimeout(() => {
      if (this.isDragging) { this.scheduleFidget(); return; }
      if (PetPlayer.activeAnim === 'relax') {
        PetPlayer.play('interact', () => PetPlayer.play('relax'));
        // 小动作偶尔也出个声
        if (Math.random() < 0.3) {
          const v = getRandomVoice('fidget');
          if (v) VoiceSystem.play(v);
        }
      }
      this.scheduleFidget();
    }, delay);
  },

  // 自主小范围走动：每 45-90 秒，走 3-6 秒
  scheduleAutoWalk() {
    const delay = 45000 + Math.random() * 45000;
    this.autoWalkTimer = setTimeout(() => {
      if (this.isDragging) { this.scheduleAutoWalk(); return; }
      const cur = PetPlayer.activeAnim;
      if (cur === 'relax' || cur === 'backIdle' || cur === 'idle') {
        this.doAutonomousWalk();
      }
      this.scheduleAutoWalk();
    }, delay);
  },

  async doAutonomousWalk() {
    // 检测屏幕边界，决定方向
    await this.refreshWindowBounds();
    let dir = Math.random() > 0.5 ? 1 : -1;

    if (this.screenW && this.winW) {
      // 靠近右边界 → 向左走
      if (this.windowX + this.winW > this.screenW - 80) dir = -1;
      // 靠近左边界 → 向右走
      if (this.windowX < 50) dir = 1;
    }

    this.walkDir = dir;
    PetPlayer.flipX = (dir < 0);
    PetPlayer.play('move');

    // 偶尔带一句台词
    if (Math.random() < 0.4) {
      const v = getRandomVoice('autoWalk');
      if (v) VoiceSystem.play(v);
    }

    const duration = 3000 + Math.random() * 4000;
    const step = 3;
    const stepMs = 50;

    if (this.walkTimer) clearTimeout(this.walkTimer);

    const doStep = () => {
      if (!window.electronAPI) return;
      window.electronAPI.moveWindow(step * this.walkDir, 0);
      this.windowX += step * this.walkDir;
      // 边界反弹
      if (this.screenW && this.winW) {
        if (this.windowX < 20) this.walkDir = 1;
        if (this.windowX + this.winW > this.screenW - 20) this.walkDir = -1;
        PetPlayer.flipX = (this.walkDir < 0);
      }
      this.walkTimer = setTimeout(doStep, stepMs);
    };
    this.walkTimer = setTimeout(doStep, stepMs);

    // 一定时间后停止
    if (this.walkStopTimer) clearTimeout(this.walkStopTimer);
    this.walkStopTimer = setTimeout(() => {
      this.stopWalk();
      PetPlayer.flipX = false;
      PetPlayer.play('relax');
    }, duration);
  },

  startAutonomousWalk(durationSec) {
    this.walkDir = Math.random() > 0.5 ? 1 : -1;
    PetPlayer.flipX = (this.walkDir < 0);
    PetPlayer.play('move');

    const step = 4;
    const stepMs = 50;

    if (this.walkTimer) clearTimeout(this.walkTimer);

    const doStep = () => {
      if (!window.electronAPI) return;
      window.electronAPI.moveWindow(step * this.walkDir, 0);
      this.windowX += step * this.walkDir;
      if (this.screenW && this.winW) {
        if (this.windowX < 20) this.walkDir = 1;
        if (this.windowX + this.winW > this.screenW - 20) this.walkDir = -1;
        PetPlayer.flipX = (this.walkDir < 0);
      }
      this.walkTimer = setTimeout(doStep, stepMs);
    };
    this.walkTimer = setTimeout(doStep, stepMs);

    this.walkStopTimer = setTimeout(() => {
      this.stopWalk();
      PetPlayer.flipX = false;
      PetPlayer.play('relax');
    }, durationSec * 1000);
  },

  stopWalk() {
    if (this.walkTimer) { clearTimeout(this.walkTimer); this.walkTimer = null; }
    if (this.walkStopTimer) { clearTimeout(this.walkStopTimer); this.walkStopTimer = null; }
  },

  // 坐下：30 秒无操作
  scheduleSit() {
    this.sitTimer = setTimeout(() => {
      if (this.isDragging) { this.scheduleSit(); return; }
      if (PetPlayer.activeAnim === 'relax') {
        PetPlayer.play('sit');
        const v = getRandomVoice('sitDown');
        if (v) VoiceSystem.speak(v);
      }
    }, 30000);
  },

  // 闲聊：2 分钟无操作
  scheduleChat() {
    this.chatTimer = setTimeout(() => {
      if (this.isDragging) { this.scheduleChat(); return; }
      PetPlayer.play('interact', () => PetPlayer.play('relax'));
      const v = getRandomVoice('idleChat');
      if (v) VoiceSystem.speak(v);
      this.scheduleChat();
    }, 120000);
  },

  // 睡觉：5 分钟无操作
  scheduleSleep() {
    this.sleepTimer = setTimeout(() => {
      if (this.isDragging) { this.scheduleSleep(); return; }
      PetPlayer.play('sleep');
      const v = getRandomVoice('goSleep');
      if (v) VoiceSystem.play(v);
    }, 300000);
  },

  // === 对话气泡 ===
  updateBubblePosition() {
    if (!this.bubble) return;
    const box = PetPlayer.charBox;
    if (box.top > 0 && box.top < this.canvas.offsetHeight) {
      const top = Math.max(2, box.top - 10);
      const cx = (box.left + box.right) / 2;
      this.bubble.style.top = `${top}px`;
      this.bubble.style.left = `${cx}px`;
    }
  },

  showBubble(text, duration) {
    if (!this.bubble || !this.bubbleText) return;
    this.updateBubblePosition();

    this.bubbleText.textContent = '';
    this.bubble.classList.remove('hidden');
    this.bubble.classList.add('show');

    let i = 0;
    const typeSpeed = 50;
    const typeChar = () => {
      if (i < text.length) {
        this.bubbleText.textContent += text[i];
        i++;
        setTimeout(typeChar, typeSpeed);
      }
    };
    typeChar();

    if (this.bubbleHideTimer) clearTimeout(this.bubbleHideTimer);
    this.bubbleHideTimer = setTimeout(() => this.hideBubble(), duration || Math.max(2500, text.length * 100));
  },

  hideBubble() {
    if (this.bubble) {
      this.bubble.classList.remove('show');
      this.bubble.classList.add('hidden');
      if (this.bubbleText) this.bubbleText.textContent = '';
    }
  },

  // === 右键菜单 ===
  showContextMenu(e) {
    const rect = this.canvas.getBoundingClientRect();
    this.contextMenu.style.left = `${e.clientX - rect.left}px`;
    this.contextMenu.style.top = `${e.clientY - rect.top}px`;
    this.contextMenu.classList.remove('hidden');
    this.contextMenu.classList.add('show');
  },

  hideContextMenu() {
    this.contextMenu.classList.remove('show');
    this.contextMenu.classList.add('hidden');
  },

  // === 启动 ===
  startup() {
    PetPlayer.play('start', () => PetPlayer.play('relax'));
    setTimeout(() => {
      const v = getRandomVoice('startup');
      if (v) VoiceSystem.speak(v);
    }, 600);
  },
};

window.showBubble = (text, duration) => Interactions.showBubble(text, duration);
