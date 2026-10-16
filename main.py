"""麦哲伦桌面宠物 —— 入口"""
import sys, os

# PyInstaller 打包后资源在临时目录 _MEIPASS
def _base_dir():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, _base_dir())

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QAction, QPainter, QColor, QBrush, QPen
from PySide6.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu

from pet_window import PetWindow


class SpeechBubble(QLabel):
    """对话气泡 —— 独立置顶窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setStyleSheet("""
            QLabel {
                padding: 10px 16px;
                font-size: 14px; color: #fff;
            }""")
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setWordWrap(True)
        self.setMaximumWidth(300)
        self.hide()
        self._hide_timer = QTimer(self, singleShot=True, timeout=self.hide)
        self._type_timer = QTimer(self, timeout=self._type_next)
        self._char_idx = 0
        self._full = ""

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor(0, 0, 0, 180))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(self.rect(), 12, 12)
        p.end()
        super().paintEvent(event)

    def show_text(self, text, duration=3000):
        self._full = text
        self._char_idx = 0
        self.setText("")
        self._type_timer.start(50)
        self._hide_timer.start(duration)

    def _type_next(self):
        if self._char_idx < len(self._full):
            self._char_idx += 1
            self.setText(self._full[:self._char_idx])
            self.adjustSize()
            self.show()
        else:
            self._type_timer.stop()


def _load_icon():
    """加载托盘图标"""
    icon_path = os.path.join(_base_dir(), "立绘_麦哲伦_2.png")
    if os.path.exists(icon_path):
        pix = QPixmap(icon_path)
        if not pix.isNull():
            # 缩到 64x64 做托盘图标
            return QIcon(pix.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    return QIcon()


def _setup_tray(app, pet, bubble):
    icon = _load_icon()
    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("麦哲伦 · 桌面宠物")

    menu = QMenu()
    menu.setStyleSheet(
        "QMenu { background: white; border:1px solid #ccc; padding:4px; }"
        "QMenu::item { padding:6px 20px; }"
        "QMenu::item:selected { background:#e8f0fe; color:#1a73e8; }")

    a_show = QAction("显示 / 隐藏", menu)
    a_voice = QAction("🔊 关闭语音", menu)
    a_talk = QAction("说句话", menu)
    a_skill = QAction("放无人机", menu)
    a_quit = QAction("退出", menu)
    for a in (a_show, a_voice, a_talk, a_skill):
        menu.addAction(a)
    menu.addSeparator()
    menu.addAction(a_quit)
    tray.setContextMenu(menu)

    def toggle_visible():
        if pet.isVisible():
            pet.hide()
            bubble.hide()
        else:
            pet.show()
            pet.raise_()

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.Trigger:  # 左键单击
            toggle_visible()
        elif reason == QSystemTrayIcon.DoubleClick:
            pet.show()
            pet.raise_()

    a_show.triggered.connect(toggle_visible)
    a_voice.triggered.connect(lambda: (
        pet.toggle_voice(),
        a_voice.setText("🔊 开启语音" if not pet.voice_enabled else "🔇 关闭语音")
    ))
    a_talk.triggered.connect(lambda: (pet.show(), pet.raise_(),
                                       pet.behavior.on_manual_scene("sceneGreet")))
    a_skill.triggered.connect(lambda: (pet.show(), pet.raise_(),
                                        pet._trigger_drone_show(3)))

    def on_quit():
        pet.behavior.stop()
        pet._play_anim("die")
        QTimer.singleShot(1200, app.quit)

    a_quit.triggered.connect(on_quit)
    tray.activated.connect(on_tray_activated)
    tray.show()
    return tray


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(_load_icon())

    pet = PetWindow()
    bubble = SpeechBubble()
    tray = _setup_tray(app, pet, bubble)
    # 阻止 tray 被垃圾回收
    app._tray = tray

    def on_bubble(text, dur):
        bubble.show_text(text, dur)

    pet.bubble_signal.connect(on_bubble)
    pet.hidden_signal.connect(bubble.hide)

    # 气泡位置更新
    def update_bubble():
        if not (bubble.isVisible() and pet._char_rect):
            return
        r = pet._char_rect  # (left, top, right, bottom) in frame coords
        rgba = pet._last_rgba
        if rgba is None:
            return
        fh, fw = rgba.shape[:2]
        scale = min(pet.width() / fw, pet.height() / fh)
        dw, dh = int(fw * scale), int(fh * scale)
        dx = (pet.width() - dw) // 2
        dy = (pet.height() - dh) // 2
        cx_frame = (r[0] + r[2]) / 2
        if pet.flip_x:
            cx_frame = fw - cx_frame
        ctop = pet.y() + dy + int(r[1] * scale)
        cleft = pet.x() + dx + int(cx_frame * scale)
        # 人物在左半屏 → 气泡在右；右半屏 → 气泡在左
        screen_cx = screen.width() // 2
        if cleft < screen_cx:
            bx = cleft + 30
        else:
            bx = cleft - bubble.width() - 30
        bubble.move(bx, max(0, ctop - bubble.height() // 2))

    bubble_pos_timer = QTimer()
    bubble_pos_timer.timeout.connect(update_bubble)
    bubble_pos_timer.start(120)

    # 右键菜单
    pet.setContextMenuPolicy(Qt.CustomContextMenu)
    pet.customContextMenuRequested.connect(lambda _: pet.show_context_menu())

    # 位置
    screen = app.primaryScreen().availableGeometry()
    pet.move(screen.right() - pet.width() - 20, screen.bottom() - pet.height() - 40)
    pet.show()
    pet.raise_()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
