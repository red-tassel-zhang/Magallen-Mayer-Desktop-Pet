"""透明桌面宠物窗口 —— 全部功能"""
import ctypes, random, time
import numpy as np
from ctypes import wintypes
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QCursor, QTransform
from PySide6.QtWidgets import QWidget, QMenu, QApplication

from data import (get_anim_path, get_green_anim_path, get_drone_path,
                  get_green_drone_path, random_voice, pick_voice,
                  pick_voice_from, DRONE_TYPES, ANIM_LOOP)
from animation_player import AnimationPlayer
from voice_player import VoicePlayer
from behavior import BehaviorTree

WM_NCHITTEST = 0x0084
HTTRANSPARENT = -1
HTCLIENT = 1

WALK_POOL = ["move"]
CLICK_POOL = ["interact"]
TALK_POOL = ["interact"]


class PetWindow(QWidget):
    bubble_signal = Signal(str, int)
    hidden_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self.w, self.h = 500, 650
        self.resize(self.w, self.h)

        # 播放器
        self.player = AnimationPlayer()
        self.voice = VoicePlayer()

        # 无人机（可变数量，1-3台）
        self._drones = []
        self._drone_types = []       # 当前召唤的型号列表
        self._drone_frames = []
        self._drone_session = 0
        self._drone_start_time = 0.0  # 用于浮动动画计时

        # 状态
        self.skin = "default"
        self.voice_enabled = True
        self.current_anim = "relax"
        self.pending_anim = None
        self.flip_x = False
        self._last_rgba = None
        self._char_rect = None

        # 鼠标
        self.dragging = False
        self.drag_start = None
        self.drag_has_moved = False
        self.last_click_time = 0
        self._click_streak = 0
        self._last_streak_time = 0
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._check_single_click)

        # 走路定时器
        self._walk_timer = None
        self._walk_stop_timer = None

        # 渲染 ~25fps
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

        # 行为树 —— 情绪 + 场景调度
        self.behavior = BehaviorTree(self)

        # 启动
        self._play_anim("start", pending="relax")
        QTimer.singleShot(600, lambda: self._say("startup"))

    def hideEvent(self, event):
        self.voice.stop()
        self.hidden_signal.emit()
        super().hideEvent(event)

    # ========== 动画 ==========
    def _play_anim(self, name, pending=None, loop=None):
        path = get_green_anim_path(self.skin, name) or get_anim_path(self.skin, name)
        if not path:
            return False
        is_loop = loop if loop is not None else (name in ANIM_LOOP)
        if not self.player.load(path, loop=is_loop):
            return False
        self.current_anim = name
        self.pending_anim = pending
        return True

    def _pick_anim(self, pool, pending="relax"):
        """从池中随机选一个动画播放，失败则用 relax"""
        name = random.choice(pool)
        if not self._play_anim(name, pending=pending):
            self._play_anim("relax")

    def _pick_available_anim(self, pool, pending="relax"):
        """Choose only clips present for the current skin."""
        choices = [name for name in pool if get_anim_path(self.skin, name)]
        self._pick_anim(choices or ["relax"], pending=pending)

    def switch_skin(self, skin_name):
        if skin_name not in ("default", "frosty"):
            return
        self.skin = skin_name
        self._play_anim("relax")

    def _trigger_drone_show(self, count=3, attack=True, duration=4000):
        """供 BehaviorTree 场景调用：召唤 count 台无人机
        count: 1/2/3 台
        attack: 是否触发攻击动画（False 只盘旋）
        duration: ms 后撤退
        """
        session = self._show_drones(count)
        if attack:
            QTimer.singleShot(700, lambda s=session: self._drone_attack(s))
        QTimer.singleShot(duration, lambda s=session: self._hide_drones(s))
        return session

    def _show_drones(self, count=3):
        self._drone_session += 1
        session = self._drone_session
        count = max(1, min(3, int(count)))
        # 从 DRONE_TYPES 里随机选 count 个不重复的型号
        types = random.sample(DRONE_TYPES, count)
        self._drone_types = types
        # 释放之前的
        for d in self._drones:
            d.release()
        from animation_player import AnimationPlayer as AP
        self._drones = [AP() for _ in types]
        for i, drone in enumerate(self._drones):
            dt = types[i]
            path = (get_green_drone_path(self.skin, dt, "Start")
                    or get_drone_path(self.skin, dt, "Start")
                    or get_drone_path("default", dt, "Idle"))
            if path:
                drone.load(path, loop=False)
        self._drone_frames = []
        self._drone_start_time = time.time()
        QTimer.singleShot(500, lambda s=session: self._set_drone_pose("Idle", s))
        return session

    def _set_drone_pose(self, pose, session=None):
        if session is not None and session != self._drone_session:
            return
        for i, drone in enumerate(self._drones):
            dt = self._drone_types[i] if i < len(self._drone_types) else DRONE_TYPES[i]
            path = (get_green_drone_path(self.skin, dt, pose)
                    or get_drone_path(self.skin, dt, pose))
            if path:
                drone.load(path, loop=(pose == "Idle"))

    def _drone_attack(self, session=None):
        if session is not None and session != self._drone_session:
            return
        for i, drone in enumerate(self._drones):
            dt = self._drone_types[i] if i < len(self._drone_types) else DRONE_TYPES[i]
            path = (get_green_drone_path(self.skin, dt, "Attack")
                    or get_drone_path(self.skin, dt, "Attack"))
            if path:
                drone.load(path, loop=False)

    def _hide_drones(self, session=None):
        if session is not None and session != self._drone_session:
            return
        self._set_drone_pose("Die", session)
        QTimer.singleShot(600, lambda s=session: self._release_drones(s))

    def _release_drones(self, session=None):
        if session is not None and session != self._drone_session:
            return
        for d in self._drones:
            d.release()
        self._drones = []
        self._drone_types = []
        self._drone_frames = []

    # ========== 语音 ==========
    def _say(self, key):
        """按行为类别抽语音"""
        path, text, dur = random_voice(key)
        self._speak(path, text, dur)

    def _say_file(self, filename):
        """指定文件名说一句（用于场景精确对齐）"""
        path, text, dur = pick_voice(filename)
        self._speak(path, text, dur)
        return dur

    def _say_from(self, pool):
        """从候选文件名池抽一条"""
        path, text, dur = pick_voice_from(pool)
        self._speak(path, text, dur)
        return dur

    def _speak(self, path, text, dur):
        if not self.isVisible():
            return
        if text:
            bubble_ms = int(max(2000, dur * 1000 + 800))
            self.bubble_signal.emit(text, bubble_ms)
        if path and self.voice_enabled:
            self.voice.play(path)

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        if not self.voice_enabled:
            self.voice.stop()

    # ========== 渲染 ==========
    def _tick(self):
        rgba = self.player.read_frame()
        if rgba is not None:
            # Some Move clips contain fully transparent transition frames. Keep
            # the last visible pose so the character does not appear to vanish.
            visible = np.count_nonzero(rgba[:, :, 3])
            if visible > rgba.shape[0] * rgba.shape[1] * 0.002 or self._last_rgba is None:
                self._last_rgba = rgba
            h, w = rgba.shape[:2]
            alpha = rgba[:, :, 3]
            rows, cols = alpha.any(axis=1), alpha.any(axis=0)
            if rows.any() and cols.any():
                self._char_rect = (
                    int(cols.argmax()), int(rows.argmax()),
                    int(len(cols) - cols[::-1].argmax()),
                    int(len(rows) - rows[::-1].argmax()),
                )

        # 无人机帧：按当前台数重排位置 + 正弦浮动
        self._drone_frames = []
        n = len(self._drones)
        elapsed = time.time() - self._drone_start_time if self._drone_start_time else 0.0
        for i, drone in enumerate(self._drones):
            if not drone.is_loaded():
                continue
            f = drone.read_frame()
            if f is None:
                continue
            if n == 1:
                base_x, base_y = 0, -100
            elif n == 2:
                base_x, base_y = -70 + i * 140, -90
            else:  # n == 3
                base_x = -80 + i * 80
                base_y = -80 - abs(i - 1) * 30
            # 每台无人机不同相位的浮动，避免同步
            phase = i * 1.7 + elapsed * 2.0
            float_x = int(4 * np.sin(phase))
            float_y = int(6 * np.sin(phase * 0.7 + 1.0))
            self._drone_frames.append((f, base_x + float_x, base_y + float_y))

        # 一次性动画结束 → 切 pending
        if self.player.finished and self.pending_anim:
            self._play_anim(self.pending_anim)
            self.pending_anim = None

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        cw, ch = self.width(), self.height()

        # 角色
        if self._last_rgba is not None:
            rgba = self._last_rgba
            h, w = rgba.shape[:2]
            scale = min(cw / w, ch / h)
            dw, dh = int(w * scale), int(h * scale)
            dx, dy = (cw - dw) // 2, (ch - dh) // 2
            qimg = QImage(rgba.data, w, h, w * 4, QImage.Format_RGBA8888)
            pix = QPixmap.fromImage(qimg)
            if self.flip_x:
                # PySide6 exposes mirroring through QTransform rather than the
                # removed QPixmap.MirrorHorizontally enum.
                pix = pix.transformed(QTransform().scale(-1, 1))
            p.drawPixmap(dx, dy, dw, dh, pix)

        # 无人机
        for frame, off_x, off_y in self._drone_frames:
            fh, fw = frame.shape[:2]
            ds = 0.5
            fdw, fdh = int(fw * ds), int(fh * ds)
            fdx = cw // 2 + off_x - fdw // 2
            fdy = ch // 2 + off_y - fdh // 2
            qimg = QImage(frame.data, fw, fh, fw * 4, QImage.Format_RGBA8888)
            pix = QPixmap.fromImage(qimg)
            p.drawPixmap(fdx, fdy, fdw, fdh, pix)

        p.end()

    # ========== 点击穿透 ==========
    def nativeEvent(self, event_type, message):
        if event_type in (b"windows_generic_MSG", "windows_generic_MSG"):
            msg = wintypes.MSG.from_address(message.__int__())
            if msg.message == WM_NCHITTEST:
                pos = QCursor.pos()
                local = self.mapFromGlobal(pos)
                x, y = local.x(), local.y()
                if x < 0 or y < 0 or x >= self.w or y >= self.h:
                    return False, 0

                # 检查角色像素（阈值40避开半透明边缘）
                if self._last_rgba is not None:
                    rgba = self._last_rgba
                    h, w = rgba.shape[:2]
                    scale = min(self.w / w, self.h / h)
                    dw, dh = int(w * scale), int(h * scale)
                    dx, dy = (self.w - dw) // 2, (self.h - dh) // 2
                    fx = int((x - dx) / scale)
                    fy = int((y - dy) / scale)
                    if self.flip_x:
                        fx = w - 1 - fx
                    if 0 <= fx < w and 0 <= fy < h and rgba[fy, fx, 3] > 40:
                        return True, HTCLIENT

                # 检查无人机像素
                for frame, off_x, off_y in self._drone_frames:
                    fh, fw = frame.shape[:2]
                    ds = 0.5
                    fdw, fdh = int(fw * ds), int(fh * ds)
                    fdx = self.w // 2 + off_x - fdw // 2
                    fdy = self.h // 2 + off_y - fdh // 2
                    dfx, dfy = int((x - fdx) / ds), int((y - fdy) / ds)
                    if 0 <= dfx < fw and 0 <= dfy < fh and frame[dfy, dfx, 3] > 40:
                        return True, HTCLIENT

                return True, HTTRANSPARENT
        return False, 0

    # ========== 鼠标 ==========
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start = e.globalPosition().toPoint()
            self.drag_has_moved = False

    def mouseMoveEvent(self, e):
        if not self.dragging:
            return
        d = e.globalPosition().toPoint() - self.drag_start
        if abs(d.x()) > 3 or abs(d.y()) > 3:
            self.drag_has_moved = True
        if self.drag_has_moved:
            self.move(self.pos() + d)
            self.drag_start = e.globalPosition().toPoint()

    def mouseReleaseEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        self.dragging = False
        if not self.drag_has_moved:
            t = time.time()
            if self.last_click_time > 0 and t - self.last_click_time < 0.35:
                self._click_timer.stop()
                self._on_double_click()
                self.last_click_time = 0
                self._click_streak = 0
            else:
                self.last_click_time = t
                self._click_timer.start(360)
        # 拖拽后从 sit/sleep 醒来
        if self.current_anim in ("sit", "sleep"):
            self._play_anim("relax")
        self.behavior.on_user_activity()

    def _check_single_click(self):
        if self.last_click_time <= 0:
            return
        if time.time() - self.last_click_time >= 0.35:
            self.last_click_time = 0
            self._on_click()

    def _on_click(self):
        # 连击奖励：3连击触发撒娇场景
        now = time.time()
        if now - self._last_streak_time < 1.2:
            self._click_streak += 1
        else:
            self._click_streak = 1
        self._last_streak_time = now

        if self._click_streak >= 3:
            self._click_streak = 0
            self.behavior.on_manual_scene("sceneWave")
            self._say("sceneCombo")
            return

        self._pick_anim(CLICK_POOL, pending="relax")
        self._say("click")

    def _on_double_click(self):
        self._pick_anim(["skill", "attack"], pending="relax")
        self._trigger_drone_show()
        self._say("doubleClick")

    def _perform_attack(self, with_drones=False):
        self._stop_walk()
        self._pick_available_anim(["attack", "skill"], pending="relax")
        if with_drones:
            self._trigger_drone_show()
        self._say("menuSkill")

    # ========== 走动 ==========
    def _start_walk(self, sec):
        self._stop_walk()
        screen = QApplication.primaryScreen().availableGeometry()
        min_x = screen.left()
        max_x = screen.right() - self.width() + 1
        # 起步方向：优先朝空间更大的一侧走
        left_space = self.x() - min_x
        right_space = max_x - self.x()
        self._walk_dir = 1 if right_space >= left_space else -1
        self.flip_x = (self._walk_dir < 0)
        self._pick_anim(WALK_POOL)
        step = 2

        def step_loop():
            if self._walk_timer is None:
                return
            next_x = self.x() + step * self._walk_dir
            if next_x < min_x or next_x > max_x:
                self._walk_dir *= -1
                self.flip_x = self._walk_dir < 0
                next_x = max(min_x, min(max_x, next_x))
            self.move(next_x, self.y())

        self._walk_timer = QTimer(self)
        self._walk_timer.timeout.connect(step_loop)
        self._walk_timer.start(50)
        self._walk_stop_timer = QTimer(self)
        self._walk_stop_timer.setSingleShot(True)
        self._walk_stop_timer.timeout.connect(self._stop_walk)
        self._walk_stop_timer.start(sec * 1000)

    def _stop_walk(self):
        if isinstance(self._walk_timer, QTimer):
            self._walk_timer.stop()
            self._walk_timer.deleteLater()
        if isinstance(self._walk_stop_timer, QTimer):
            self._walk_stop_timer.stop()
            self._walk_stop_timer.deleteLater()
        self._walk_timer = None
        self._walk_stop_timer = None
        if self.current_anim == "move":
            self.flip_x = False
            self._play_anim("relax")

    # ========== 右键菜单 ==========
    def show_context_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: white; border:1px solid #ccc; padding:4px; }"
            "QMenu::item { padding:6px 20px; }"
            "QMenu::item:selected { background:#e8f0fe; color:#1a73e8; }")

        a_talk = menu.addAction("💬 说句话")
        a_skill = menu.addAction("🚁 放出无人机")
        a_attack = menu.addAction("⚡ 释放技能")
        a_special = None
        if self.skin == "frosty":
            a_special = menu.addAction("❄️ 特殊动作")
        a_walk = menu.addAction("🚶 走一走")
        a_sit = menu.addAction("🪑 坐下")
        a_sleep = menu.addAction("😴 睡觉")
        menu.addSeparator()
        voice_label = "🔇 关闭语音" if self.voice_enabled else "🔊 开启语音"
        a_voice = menu.addAction(voice_label)
        skin_label = "👗 换装·冰霜雪" if self.skin == "default" else "👗 换回默认"
        a_skin = menu.addAction(skin_label)
        menu.addSeparator()
        a_hide = menu.addAction("👻 隐藏（可从托盘唤回）")
        a_quit = menu.addAction("❌ 退出")

        act = menu.exec(QCursor.pos())
        if not act:
            return
        # 从 sit/sleep 唤醒
        if self.current_anim in ("sit", "sleep"):
            self._play_anim("relax")
        self.behavior.on_user_activity()

        if act == a_talk:
            self._pick_anim(TALK_POOL, pending="relax")
            self._say("menuTalk")
        elif act == a_skill:
            self._perform_attack(with_drones=True)
        elif act == a_attack:
            self._perform_attack()
        elif act == a_special:
            self._stop_walk()
            self._pick_available_anim(["special", "skill", "attack"], pending="relax")
            self._say("menuSkill")
        elif act == a_walk:
            self._start_walk(8)
            self._say("menuWalk")
        elif act == a_sit:
            self._stop_walk()
            self._play_anim("sit")
            self._say("menuSit")
        elif act == a_sleep:
            self._stop_walk()
            self._play_anim("sleep")
            self._say("menuSleep")
        elif act == a_voice:
            self.toggle_voice()
        elif act == a_skin:
            self.skin = "frosty" if self.skin == "default" else "default"
            self._play_anim("relax")
            self._say("skinSwitch")
        elif act == a_hide:
            self.hide()
        elif act == a_quit:
            self.behavior.stop()
            self._play_anim("die")
            QTimer.singleShot(1200, QApplication.quit)
