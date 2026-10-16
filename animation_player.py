"""WebM 动画播放器 —— 帧缓存 + numpy 色度键"""
import cv2
import numpy as np
import os


class AnimationPlayer:
    # Keep loop animation memory bounded; WebM frames in this project are large.
    MAX_CACHE_BYTES = 96 * 1024 * 1024
    MAX_FRAME_DIM = 560

    def __init__(self):
        self.cap = None
        self.loop = False
        self.width = self.height = 0
        self.fps = 30
        self.rgba_frame = None
        self.bg_color = None
        self.finished = False
        # 帧缓存（循环动画用）
        self._cache = []
        self._cache_idx = 0
        self._cache_enabled = False
        self.green_screen = False

    def load(self, path, loop=False):
        self.release()
        if not path or not os.path.exists(path):
            return False
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            self.cap = None
            return False
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.loop = loop
        parent_dir = os.path.basename(os.path.dirname(path)).lower()
        self.green_screen = parent_dir in ("bbb", "mayer")
        self.finished = False
        self.bg_color = None
        self._cache = []
        self._cache_idx = 0
        self._cache_enabled = False

        if loop:
            self._build_cache()
        return True

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self._cache = []
        self.rgba_frame = None

    def is_loaded(self):
        return self.cap is not None

    # ---- 背景采样 ----
    def _sample_bg(self, frame):
        h, w = frame.shape[:2]
        s = min(10, w // 4, h // 4)
        corners = [frame[0:s, 0:s], frame[0:s, w - s:w],
                   frame[h - s:h, 0:s], frame[h - s:h, w - s:w]]
        samples = np.vstack([c.reshape(-1, 3) for c in corners])
        lum = np.sum(samples, axis=1)
        return tuple(samples[np.argsort(lum)[len(lum) // 2]].astype(float))

    # ---- 色度键 ----
    def _chroma_key(self, frame):
        h, w = frame.shape[:2]
        if max(h, w) > self.MAX_FRAME_DIM:
            scale = self.MAX_FRAME_DIM / max(h, w)
            frame = cv2.resize(frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
        if self.green_screen:
            # Fast green-screen key: no per-pixel Euclidean distance/sqrt.
            b, g, r = cv2.split(frame)
            green_strength = g.astype(np.int16) - ((r.astype(np.int16) + b.astype(np.int16)) >> 1)
            alpha = np.full(green_strength.shape, 255, dtype=np.uint8)
            alpha[green_strength >= 80] = 0
            fade = (green_strength >= 30) & (green_strength < 80)
            alpha[fade] = ((80 - green_strength[fade]) * 5).astype(np.uint8)
        else:
            # Conservative fallback for legacy dark-background clips.
            if self.bg_color is None:
                self.bg_color = self._sample_bg(frame)
            bg = np.array(self.bg_color, dtype=np.float32)
            diff = frame.astype(np.float32) - bg
            dist = np.sqrt(np.sum(diff * diff, axis=2))
            alpha = np.full(dist.shape, 255, dtype=np.uint8)
            alpha[dist <= 32] = 0
            fade = (dist > 32) & (dist < 78)
            alpha[fade] = ((dist[fade] - 32) / 46 * 255).astype(np.uint8)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return np.dstack([rgb, alpha])

    # ---- 预构建缓存 ----
    def _build_cache(self):
        self._cache = []
        if not self.cap:
            return
        # 先预估：帧数 × 单帧 rgba 字节，超过预算直接走流式
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        w = self.width
        h = self.height
        if max(h, w) > self.MAX_FRAME_DIM:
            s = self.MAX_FRAME_DIM / max(h, w)
            w, h = int(w * s), int(h * s)
        est = frame_count * w * h * 4
        if frame_count > 0 and est > self.MAX_CACHE_BYTES:
            self._cache_enabled = False
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            self._cache.append(self._chroma_key(frame))
        self._cache_enabled = bool(self._cache)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # ---- 读帧 ----
    def read_frame(self):
        if not self.is_loaded():
            return None
        # 非循环动画播完后短路，避免 cv2 反复空读
        if self.finished and not self.loop:
            return None

        # 循环动画走缓存
        if self.loop and self._cache_enabled and self._cache:
            self.rgba_frame = self._cache[self._cache_idx]
            self._cache_idx = (self._cache_idx + 1) % len(self._cache)
            self._update_char_box()
            return self.rgba_frame

        # 非循环动画实时处理
        ret, frame = self.cap.read()
        if not ret:
            if self.loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                if not ret:
                    self.finished = True
                    return None
                self.finished = False
            else:
                self.finished = True
                return None
        self.rgba_frame = self._chroma_key(frame)
        self._update_char_box()
        return self.rgba_frame

    def _update_char_box(self):
        """记录角色包围盒（原始帧坐标）"""
        rgba = self.rgba_frame
        if rgba is None:
            return
        alpha = rgba[:, :, 3]
        rows = alpha.any(axis=1)
        cols = alpha.any(axis=0)
        if rows.any() and cols.any():
            self.char_top = int(np.argmax(rows))
            self.char_bottom = int(len(rows) - np.argmax(rows[::-1]))
            self.char_left = int(np.argmax(cols))
            self.char_right = int(len(cols) - np.argmax(cols[::-1]))
        else:
            self.char_top = self.char_bottom = self.char_left = self.char_right = 0

    def restart(self):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self._cache_idx = 0
            self.finished = False
