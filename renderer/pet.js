// 动画播放器 - WebM 视频加载 + Canvas 渲染 + 智能去背景

const PetPlayer = {
  canvas: null,
  ctx: null,
  videoPool: {},
  activeAnim: null,
  activeVideo: null,
  defaultAnim: 'relax',

  onEndCallback: null,
  animFrameId: null,

  // 离屏 canvas
  offscreen: null,
  offCtx: null,

  // 背景色采样（每动画独立缓存）
  bgColorCache: {},

  // 角色可见区域包围盒（Canvas 坐标），供气泡定位
  charBox: { top: 0, left: 0, right: 0, bottom: 0 },

  // 镜像翻转（走路方向）
  flipX: false,

  init(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.offscreen = document.createElement('canvas');
    this.offCtx = this.offscreen.getContext('2d');
    this.resize();
    this.preloadAll();
  },

  resize() {
    const w = this.canvas.offsetWidth;
    const h = this.canvas.offsetHeight;
    this.canvas.width = w;
    this.canvas.height = h;
    this.offscreen.width = w;
    this.offscreen.height = h;
  },

  preloadAll() {
    for (const [name, src] of Object.entries(ANIMATIONS)) {
      const video = document.createElement('video');
      video.src = src;
      video.muted = true;
      video.loop = ANIM_LOOP[name] || false;
      video.preload = 'auto';
      video.crossOrigin = 'anonymous';
      video.setAttribute('playsinline', '');
      this.videoPool[name] = video;
      video.load();
    }
  },

  play(name, onEnd) {
    const video = this.videoPool[name];
    if (!video) return;

    this.onEndCallback = onEnd || null;

    if (this.activeAnim === name && ANIM_LOOP[name]) return;

    if (this.activeVideo) this.activeVideo.pause();

    this.activeAnim = name;
    this.activeVideo = video;

    video.currentTime = 0;
    video.loop = ANIM_LOOP[name] || false;

    if (!ANIM_LOOP[name]) {
      const handler = () => {
        if (video.currentTime >= video.duration - 0.05) {
          video.removeEventListener('timeupdate', handler);
          video.pause();
          if (this.onEndCallback) { const cb = this.onEndCallback; this.onEndCallback = null; cb(); }
          if (this.activeAnim === name) this.play(this.defaultAnim);
        }
      };
      video.addEventListener('timeupdate', handler);
    }

    video.play().catch(() => {});
  },

  getCurrentFrame() {
    if (!this.activeVideo) return null;
    if (this.activeVideo.readyState < 2) return null;
    return this.activeVideo;
  },

  // ---- 背景色采样：从四角取中位数 ----
  sampleBgColor(imageData, w, h) {
    const d = imageData.data;
    // 采样四角 10x10 区域
    const samples = [];
    const sampleSize = 10;
    const corners = [
      [0, 0], [w - sampleSize, 0],
      [0, h - sampleSize], [w - sampleSize, h - sampleSize],
    ];
    for (const [sx, sy] of corners) {
      for (let y = sy; y < sy + sampleSize && y < h; y++) {
        for (let x = sx; x < sx + sampleSize && x < w; x++) {
          const i = (y * w + x) * 4;
          samples.push([d[i], d[i + 1], d[i + 2]]);
        }
      }
    }
    if (samples.length === 0) return [0, 0, 0];

    // 按亮度排序，取中位数（排除异常值）
    samples.sort((a, b) => (a[0] + a[1] + a[2]) - (b[0] + b[1] + b[2]));
    const mid = samples[Math.floor(samples.length / 2)];
    return mid;
  },

  // 颜色距离
  colorDist(r1, g1, b1, r2, g2, b2) {
    const dr = r1 - r2, dg = g1 - g2, db = b1 - b2;
    return Math.sqrt(dr * dr + dg * dg + db * db);
  },

  // ---- 主渲染 ----
  render() {
    const video = this.getCurrentFrame();
    if (!video) {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
      return;
    }

    const vw = video.videoWidth;
    const vh = video.videoHeight;
    if (!vw || !vh) return;

    const cw = this.canvas.width;
    const ch = this.canvas.height;
    const scale = Math.min(cw / vw, ch / vh);
    const dw = Math.round(vw * scale);
    const dh = Math.round(vh * scale);
    const dx = Math.round((cw - dw) / 2);
    const dy = Math.round((ch - dh) / 2);

    // 绘制到离屏 canvas
    this.offCtx.clearRect(0, 0, cw, ch);
    this.offCtx.drawImage(video, dx, dy, dw, dh);

    const imageData = this.offCtx.getImageData(dx, dy, dw, dh);
    const pixels = imageData.data;

    // 获取背景色（采样四角，缓存）
    const cacheKey = this.activeAnim;
    if (!this.bgColorCache[cacheKey]) {
      this.bgColorCache[cacheKey] = this.sampleBgColor(imageData, dw, dh);
    }
    const [bgR, bgG, bgB] = this.bgColorCache[cacheKey];

    const keyDist = 28;   // 完全透明：与背景色距离 < 此值（收紧以保护轮廓）
    const fadeDist = 35;  // 过渡区宽度（加宽以柔化边缘）

    // 角色包围盒
    let top = dh, left = dw, right = 0, bottom = 0;

    for (let i = 0; i < pixels.length; i += 4) {
      const r = pixels[i];
      const g = pixels[i + 1];
      const b = pixels[i + 2];
      const dist = this.colorDist(r, g, b, bgR, bgG, bgB);

      if (dist <= keyDist) {
        pixels[i + 3] = 0;
      } else if (dist < keyDist + fadeDist) {
        const ratio = (dist - keyDist) / fadeDist;
        pixels[i + 3] = Math.round(pixels[i + 3] * ratio);
      }

      // 跟踪包围盒
      if (pixels[i + 3] > 0) {
        const px = (i / 4) % dw;
        const py = Math.floor((i / 4) / dw);
        if (px < left) left = px;
        if (px > right) right = px;
        if (py < top) top = py;
        if (py > bottom) bottom = py;
      }
    }

    // 更新角色包围盒（Canvas 坐标系）
    if (top <= bottom) {
      this.charBox = {
        top: dy + top,
        left: dx + left,
        right: dx + right,
        bottom: dy + bottom,
      };
    }

    this.ctx.clearRect(0, 0, cw, ch);

    if (this.flipX) {
      // 镜像绘制
      this.ctx.save();
      this.ctx.translate(cw, 0);
      this.ctx.scale(-1, 1);
      this.ctx.putImageData(imageData, cw - dx - dw, dy);
      this.ctx.restore();
    } else {
      this.ctx.putImageData(imageData, dx, dy);
    }
  },

  stop() {
    if (this.activeVideo) {
      this.activeVideo.pause();
      this.activeVideo = null;
      this.activeAnim = null;
    }
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
  },
};
