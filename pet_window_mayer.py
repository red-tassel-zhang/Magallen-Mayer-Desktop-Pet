"""透明桌面宠物窗口 —— 梅尔"""
import ctypes, random, time
import numpy as np
from ctypes import wintypes
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap, QPainter, QCursor, QTransform
from PySide6.QtWidgets import QWidget, QMenu, QApplication

from data_mayer import (get_anim_path, get_green_anim_path, get_drone_path,
                        get_green_drone_path, random_voice, pick_voice,
                        pick_voice_from, DRONE_TYPES, ANIM_LOOP)
from animation_player import AnimationPlayer
from voice_player import VoicePlayer
from behavior_mayer import BehaviorTree

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

        self.player = AnimationPlayer()
        self.voice = VoicePlayer()

        self._drones = []
        self._drone_types = []
        self._drone_frames = []
        self._drone_session = 0
        self._drone_start_time = 0.0

        self.skin = "default"
        self.voice_enabled = True
        self.current_anim = "relax"
        self.pending_anim = None
        self.flip_x = False
        self._last_rgba = None
        self._char_rect = None

        self.dragging = False
        self.drag_start = None
        self.drag_has_moved = False
        self.last_click_time = 0
        self._click_streak = 0
        self._last_streak_time = 0
        self._click_timer = QTimer(self)
        self._click_timer.setSingleShot(True)
        self._click_timer.timeout.connect(self._check_single_click)

        self._walk_timer = None
        self._walk_stop_timer = None

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)

        self.behavior = BehaviorTree(self)

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
        name = random.choice(pool)
        if not self._play_anim(name, pending=pending):
            self._play_anim("relax")

    def _pick_available_anim(self, pool, pending="relax"):
        choices = [name for name in pool if get_anim_path(self.skin, name)]
        self._pick_anim(choices or ["relax"], pending=pending)

    def switch_skin(self, skin_name):
        if skin_name not in ("default", "garden"):
            return
        self.skin = skin_name
        self._play_anim("relax")

    def _trigger_drone_show(self, count=1, attack=True, duration=4000):
        session = self._show_drones(count)
        if attack:
            QTimer.singleShot(700, lambda s=session: self._drone_attack(s))
        QTimer.singleShot(duration, lambda s=session: self._hide_drones(s))
        return session

    def _show_drones(self, count=1):
        self._drone_session += 1
        session = self._drone_session
        # 梅尔只有一只机械水獭咪波
        types = [DRONE_TYPES[0]]
        self._drone_types = types
        for d in self._drones:
            d.release()
        from animation_player import AnimationPlayer as AP
        self._drones = [AP() for _ in types]
        dt = types[0]
        path = (get_green_drone_path(self.skin, dt, "Idle")
                or get_drone_path(self.skin, dt, "Idle"))
        if path:
            self._drones[0].load(path, loop=False)
        self._drone_frames = []
        self._drone_start_time = time.time()
        QTimer.singleShot(500, lambda s=session: self._set_drone_pose("Idle", s))
        return session

    def _set_drone_pose(self, pose, session=None):
        if session is not None and session != self._drone_session:
            return
        for i, drone in enumerate(self._drones):
            dt = self._drone_types[i] if i < len(self._drone_types) else DRONE_TYPES[0]
            path = (get_green_drone_path(self.skin, dt, pose)
                    or get_drone_path(self.skin, dt, pose))
            if path:
                drone.load(path, loop=(pose == "Idle"))

    def _drone_attack(self, session=None):
        if session is not None and session != self._drone_session:
            return
        for i, drone in enumerate(self._drones):
            dt = self._drone_types[i] if i < len(self._drone_types) else DRONE_TYPES[0]
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
        path, text, dur = random_voice(key)
        self._speak(path, text, dur)

    def _say_file(self, filename):
        path, text, dur = pick_voice(filename)
        self._speak(path, text, dur)
        return dur

    def _say_from(self, pool):
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

        self._drone_frames = []
        n = len(self._drones)
        elapsed = time.time() - self._drone_start_time if self._drone_start_time else 0.0
        for i, drone in enumerate(self._drones):
            if not drone.is_loaded():
                continue
            f = drone.read_frame()
            if f is None:
                continue
            # 咪波是地面机械狗，放在角色脚边（用包围盒动态定位）
            base_x = 0
            base_y = 150  # fallback，无包围盒时使用
            if self._last_rgba is not None and self._char_rect is not None:
                r = self._char_rect  # (left, top, right, bottom) in frame coords
                fh, fw = self._last_rgba.shape[:2]
                scale = min(self.w / fw, self.h / fh)
                _, dh = int(fw * scale), int(fh * scale)
                _, dy = (self.w - int(fw * scale)) // 2, (self.h - dh) // 2
                char_feet_y = dy + int(r[3] * scale)  # 角色脚底在窗口中的 y
                otter_h = int(f.shape[0] * 0.5)  # 咪波渲染高度（ds=0.5）
                base_y = char_feet_y - self.h // 2 + otter_h // 2 - 200
            phase = i * 1.7 + elapsed * 2.5
            float_x = int(3 * np.sin(phase))
            float_y = int(2 * np.sin(phase * 0.7 + 1.0))
            self._drone_frames.append((f, base_x + float_x, base_y + float_y))

        if self.player.finished and self.pending_anim:
            self._play_anim(self.pending_anim)
            self.pending_anim = None

        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        cw, ch = self.width(), self.height()

        if self._last_rgba is not None:
            rgba = self._last_rgba
            h, w = rgba.shape[:2]
            scale = min(cw / w, ch / h)
            dw, dh = int(w * scale), int(h * scale)
            dx, dy = (cw - dw) // 2, (ch - dh) // 2
            qimg = QImage(rgba.data, w, h, w * 4, QImage.Format_RGBA8888)
            pix = QPixmap.fromImage(qimg)
            if self.flip_x:
                pix = pix.transformed(QTransform().scale(-1, 1))
            p.drawPixmap(dx, dy, dw, dh, pix)

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
        a_skill = menu.addAction("🦦 放出咪波")
        a_attack = menu.addAction("⚡ 释放技能")
        a_special = None
        if self.skin == "garden":
            a_special = menu.addAction("✨ 特殊动作")
        a_walk = menu.addAction("🚶 走一走")
        a_sit = menu.addAction("🪑 坐下")
        a_sleep = menu.addAction("😴 睡觉")
        menu.addSeparator()
        voice_label = "🔇 关闭语音" if self.voice_enabled else "🔊 开启语音"
        a_voice = menu.addAction(voice_label)
        skin_label = "👗 换装·庭院寻梦尖兵" if self.skin == "default" else "👗 换回默认"
        a_skin = menu.addAction(skin_label)
        menu.addSeparator()
        a_hide = menu.addAction("👻 隐藏（可从托盘唤回）")
        a_quit = menu.addAction("❌ 退出")

        act = menu.exec(QCursor.pos())
        if not act:
            return
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
            self._play_anim("special", pending="relax")
            self._say("skinSwitch")
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
            self.skin = "garden" if self.skin == "default" else "default"
            self._play_anim("relax")
            self._say("skinSwitch")
        elif act == a_hide:
            self.hide()
        elif act == a_quit:
            self.behavior.stop()
            self._play_anim("die")
            QTimer.singleShot(1200, QApplication.quit)
