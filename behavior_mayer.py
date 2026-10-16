"""梅尔行为树 —— 情绪 + 场景 + 微动作三层调度"""
import random
import time
from PySide6.QtCore import QTimer, QObject


# ============ 场景定义 ============
CHAT_ANIMS = ["interact", "idle"]
LONG_TALK_BEATS_15S = [
    {"at": 3500, "anim": "idle", "pending": "relax"},
    {"at": 9000, "anim": "interact", "pending": "relax"},
]
LONG_TALK_BEATS_20S = [
    {"at": 4000, "anim": "idle", "pending": "relax"},
    {"at": 10000, "anim": "interact", "pending": "relax"},
    {"at": 15500, "anim": "idle", "pending": "relax"},
]

SCENES = {
    # === 微动作 ===
    "microPoke": {
        "weight_when": {"default": 1.5, "high_social": 2.0},
        "steps": [
            {"anim": CHAT_ANIMS, "pending": "relax",
             "voice_pool": ["戳一下.wav", "选中干员1.wav", "问候.wav"],
             "wait_extra": 800},
        ],
    },
    "microStretch": {
        "weight_when": {"low_energy": 2.5, "default": 1.0},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "信赖触摸.wav", "wait_extra": 400},
        ],
    },
    "microDeploy": {
        "weight_when": {"high_energy": 1.5, "default": 1.0},
        "steps": [
            {"anim": CHAT_ANIMS, "pending": "relax",
             "voice_pool": ["部署1.wav", "部署2.wav", "选中干员2.wav"],
             "wait_extra": 500},
        ],
    },

    # === 咪波无人机场景 ===
    "sceneDroneSolo": {
        "weight_when": {"high_curiosity": 2.5, "default": 1.4},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "部署2.wav",
             "drones": 1, "wait_extra": 400},
            {"anim": "relax", "pending": "relax",
             "wait": 3500},
        ],
    },
    "sceneDronePair": {
        "weight_when": {"high_curiosity": 2.0, "high_energy": 2.0, "default": 1.0},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "行动开始.wav",
             "drones": 2, "wait_extra": 400},
            {"anim": "relax", "pending": "relax",
             "wait": 3500},
        ],
    },
    "sceneDroneCall": {
        "weight_when": {"high_curiosity": 2.5, "default": 1.2},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "行动开始.wav", "wait_extra": 300},
            {"anim": "skill", "pending": "relax",
             "voice_file": "作战中1.wav",
             "drones": 3, "wait_extra": 900},
        ],
    },
    "sceneAttack": {
        "weight_when": {"high_energy": 2.0, "default": 1.2},
        "steps": [
            {"anim": "attack", "pending": "relax",
             "voice_pool": ["作战中2.wav", "作战中3.wav", "作战中4.wav"],
             "wait_extra": 400},
        ],
    },
    "sceneGreet": {
        "weight_when": {"high_social": 2.5, "default": 1.2},
        "steps": [
            {"anim": CHAT_ANIMS, "pending": "relax",
             "voice_pool": ["问候.wav", "选中干员2.wav"],
             "wait_extra": 400},
        ],
    },
    "sceneWander": {
        "weight_when": {"high_energy": 2.0, "default": 1.0, "low_energy": 0.2},
        "steps": [
            {"voice_file": "行动出发.wav", "wait_extra": 200},
            {"walk": 5, "wait": 5200},
        ],
    },
    "sceneFacility": {
        "weight_when": {"default": 0.8, "high_curiosity": 1.5},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "进驻设施.wav", "wait_extra": 400},
        ],
    },

    # === 长场景 ===
    "sceneTaleFrost": {
        "weight_when": {"high_social": 1.8, "default": 0.5},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "信赖提升后交谈1.wav",
             "beats": LONG_TALK_BEATS_15S,
             "wait_extra": 500},
        ],
    },
    "sceneTaleEve": {
        "weight_when": {"high_social": 1.5, "default": 0.6},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "交谈3.wav",
             "beats": [{"at": 4000, "anim": "idle", "pending": "relax"}],
             "wait_extra": 400},
        ],
    },
    "sceneTaleGift": {
        "weight_when": {"high_social": 1.6, "default": 0.5},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "交谈1.wav",
             "beats": LONG_TALK_BEATS_15S,
             "wait_extra": 400},
        ],
    },
    "sceneTaleDaDi": {
        "weight_when": {"high_social": 1.5, "default": 0.5},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "交谈2.wav",
             "beats": LONG_TALK_BEATS_20S,
             "wait_extra": 400},
        ],
    },
    "sceneTaleMayer": {
        "weight_when": {"high_social": 1.3, "default": 0.4},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "晋升后交谈1.wav",
             "beats": LONG_TALK_BEATS_15S,
             "wait_extra": 500},
        ],
    },
    "sceneTaleFlower": {
        "weight_when": {"high_social": 1.4, "default": 0.5},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "信赖提升后交谈2.wav",
             "beats": LONG_TALK_BEATS_15S,
             "wait_extra": 400},
        ],
    },
    "sceneTaleInvite": {
        "weight_when": {"high_social": 1.2, "default": 0.4},
        "steps": [
            {"anim": "interact", "pending": "relax",
             "voice_file": "信赖提升后交谈3.wav",
             "beats": LONG_TALK_BEATS_20S,
             "wait_extra": 400},
        ],
    },

    # === 庭院寻梦尖兵皮肤专属 ===
    "sceneSpecial": {
        "weight_when": {"skin_garden": 3.0, "default": 0.0},
        "steps": [
            {"anim": "special", "pending": "relax",
             "voice_file": "精英化晋升1.wav", "wait_extra": 800},
        ],
    },

    # === 睡意状态 ===
    "sceneSit": {
        "weight_when": {"low_energy": 3.0, "default": 0.3},
        "steps": [
            {"anim": "sit", "pending": "sit",
             "voice_file": "闲置.wav", "wait_extra": 0},
        ],
        "sticky": True,
    },
    "sceneSleep": {
        "weight_when": {"very_low_energy": 5.0, "default": 0.0},
        "steps": [
            {"anim": "sleep", "pending": "sleep",
             "voice_file": "闲置.wav", "wait_extra": 0},
        ],
        "sticky": True,
    },
}


class Mood:
    """连续情绪值，范围 0~1"""
    def __init__(self):
        self.energy = 0.9
        self.social = 0.5
        self.curiosity = 0.6

    def tick(self, dt):
        self.energy = max(0.0, self.energy - dt / 600.0)
        self.curiosity = min(1.0, self.curiosity + dt / 900.0)
        self.social = max(0.0, self.social - dt / 500.0)

    def on_interact(self):
        self.energy = min(1.0, self.energy + 0.08)
        self.social = min(1.0, self.social + 0.15)
        self.curiosity = min(1.0, self.curiosity + 0.05)

    def on_scene_done(self):
        self.curiosity = max(0.0, self.curiosity - 0.15)
        self.energy = max(0.0, self.energy - 0.03)

    def snapshot(self):
        tags = ["default"]
        if self.energy < 0.15:
            tags.append("very_low_energy")
        if self.energy < 0.35:
            tags.append("low_energy")
        if self.energy > 0.7:
            tags.append("high_energy")
        if self.social > 0.6:
            tags.append("high_social")
        if self.curiosity > 0.6:
            tags.append("high_curiosity")
        return tags


class BehaviorTree(QObject):
    def __init__(self, pet):
        super().__init__(pet)
        self.pet = pet
        self.mood = Mood()

        self._scene_token = 0
        self._current_scene = None
        self._sticky = False
        self._last_tick = time.time()

        self._pulse = QTimer(self)
        self._pulse.timeout.connect(self._pulse_check)
        self._pulse.start(2000)
        self._next_fire = time.time() + random.uniform(8, 16)

    def on_user_activity(self):
        self.mood.on_interact()
        self._sticky = False
        self._current_scene = None
        self._scene_token += 1
        self._next_fire = time.time() + random.uniform(15, 30)

    def on_manual_scene(self, scene_name):
        if scene_name in SCENES:
            self._run_scene(scene_name)

    def stop(self):
        self._pulse.stop()
        self._scene_token += 1

    def _pulse_check(self):
        now = time.time()
        dt = now - self._last_tick
        self._last_tick = now
        self.mood.tick(dt)
        if self._sticky or now < self._next_fire or self._current_scene is not None:
            return
        self._pick_and_run()

    def _pick_and_run(self):
        tags = self.mood.snapshot()
        skin_tag = f"skin_{self.pet.skin}"
        if skin_tag not in tags:
            tags.append(skin_tag)

        weighted = []
        for name, spec in SCENES.items():
            w_map = spec.get("weight_when", {})
            w = 0.0
            for tag in tags:
                if tag in w_map:
                    w = max(w, w_map[tag])
            if w <= 0:
                w = w_map.get("default", 0.0)
            if w > 0:
                weighted.append((name, w))
        if not weighted:
            return

        total = sum(w for _, w in weighted)
        r = random.uniform(0, total)
        acc = 0
        chosen = weighted[0][0]
        for name, w in weighted:
            acc += w
            if r <= acc:
                chosen = name
                break
        self._run_scene(chosen)

    def _run_scene(self, name):
        spec = SCENES.get(name)
        if not spec:
            return
        self._scene_token += 1
        token = self._scene_token
        self._current_scene = name
        self._sticky = bool(spec.get("sticky"))
        self._run_step(spec["steps"], 0, token, name)

    def _run_step(self, steps, idx, token, scene_name):
        if token != self._scene_token:
            return
        if idx >= len(steps):
            self._on_scene_finished(scene_name)
            return

        step = steps[idx]
        anim = step.get("anim")
        if isinstance(anim, (list, tuple)) and anim:
            anim = random.choice(anim)
        if anim:
            self.pet._play_anim(anim, pending=step.get("pending"))
        if "drones" in step:
            self.pet._trigger_drone_show(step["drones"])
        if "walk" in step:
            self.pet._start_walk(step["walk"])

        voice_dur = 0.0
        if "voice_file" in step:
            voice_dur = self.pet._say_file(step["voice_file"]) or 0.0
        elif "voice_pool" in step:
            voice_dur = self.pet._say_from(step["voice_pool"]) or 0.0

        for beat in step.get("beats", []):
            at = beat["at"]
            b_anim = beat.get("anim")
            if isinstance(b_anim, (list, tuple)):
                b_anim = random.choice(b_anim)
            b_pending = beat.get("pending")
            def _fire(a=b_anim, p=b_pending, tk=token):
                if tk != self._scene_token or not a:
                    return
                self.pet._play_anim(a, pending=p)
            QTimer.singleShot(at, _fire)

        if "wait" in step:
            wait = step["wait"]
        else:
            wait = int(voice_dur * 1000 + step.get("wait_extra", 400))
        if wait <= 0:
            if not self._sticky:
                self._on_scene_finished(scene_name)
            return

        QTimer.singleShot(wait,
                          lambda: self._run_step(steps, idx + 1, token, scene_name))

    def _on_scene_finished(self, scene_name):
        self.mood.on_scene_done()
        self._current_scene = None
        base = 20 if self.mood.energy > 0.5 else 40
        jitter = random.uniform(0.7, 1.4)
        self._next_fire = time.time() + base * jitter
