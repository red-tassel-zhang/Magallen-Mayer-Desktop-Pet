"""资源路径映射 & 语音文字数据"""
import os
import random
import sys

# PyInstaller onefile 运行时资源在 _MEIPASS 临时目录
BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, "assets")
GREEN_ASSETS = os.path.join(BASE, "bbb")

# ========== 皮肤动画路径 ==========
def _anim_path(skin, name):
    return os.path.join(ASSETS, skin, f"麦哲伦-{_SKIN_PREFIX[skin]}-{name}-x1.webm")

_SKIN_PREFIX = {
    "default": "默认",
    "frosty": "回味冰霜雪",
}

# 动画名 -> 文件名后缀
_ANIM_MAP = {
    "relax":    "基建-Relax",
    "interact": "基建-Interact",
    "move":     "基建-Move",
    "sit":      "基建-Sit",
    "sleep":    "基建-Sleep",
    "special":  "基建-Special",   # 仅冰霜雪有
    "start":    "正面-Start",
    "idle":     "正面-Idle",
    "skill":    "正面-Skill",      # 仅默认有
    "attack":   "正面-Attack",
    "die":      "正面-Die",
    "backIdle": "背面-Idle",
    "backStart":"背面-Start",
    "backSkill":"背面-Skill",
    "backAttack":"背面-Attack",
}

# 循环动画
ANIM_LOOP = {
    "relax", "move", "idle", "backIdle", "sleep", "sit",
}

def get_anim_path(skin, anim_name):
    """获取指定皮肤 + 动画名的文件路径，不存在则 fallback 到 default"""
    suffix = _ANIM_MAP.get(anim_name)
    if not suffix:
        return None
    path = _anim_path(skin, suffix)
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        path = _anim_path("default", suffix)
        if not os.path.exists(path) or os.path.getsize(path) < 500:
            return None
    return path


def get_green_anim_path(skin, anim_name):
    """Prefer the green-screen library when a matching clip exists."""
    suffix = _ANIM_MAP.get(anim_name)
    if not suffix:
        return None
    path = os.path.join(GREEN_ASSETS, f"麦哲伦-{_SKIN_PREFIX[skin]}-{suffix}-x1.webm")
    if os.path.exists(path) and os.path.getsize(path) >= 500:
        return path
    return None


# ========== 无人机动画路径 ==========
DRONE_TYPES = ["A", "F", "L"]

def get_drone_path(skin, drone_type, anim_name):
    """获取无人机动画路径"""
    prefix = _SKIN_PREFIX.get(skin, "默认")
    filename = f"龙腾.{drone_type}-{prefix}-战斗-{anim_name}-x1.webm"
    path = os.path.join(ASSETS, "drones", drone_type, filename)
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        # fallback to default skin
        filename = f"龙腾.{drone_type}-默认-战斗-{anim_name}-x1.webm"
        path = os.path.join(ASSETS, "drones", drone_type, filename)
        if not os.path.exists(path) or os.path.getsize(path) < 500:
            return None
    return path


def get_green_drone_path(skin, drone_type, anim_name):
    """Return a green-screen drone clip when supplied in bbb."""
    prefix = _SKIN_PREFIX.get(skin, "默认")
    filename = f"龙腾.{drone_type}-{prefix}-战斗-{anim_name}-x1.webm"
    path = os.path.join(GREEN_ASSETS, filename)
    if os.path.exists(path) and os.path.getsize(path) >= 500:
        return path
    return None


# ========== 语音 ==========
VOICES = {
    "poke":     ["戳一下.wav"],
    "select":   ["选中干员1.wav", "选中干员2.wav"],
    "greet":    ["问候.wav"],
    "talk":     ["交谈1.wav", "交谈2.wav", "交谈3.wav"],
    "idle":     ["闲置.wav"],
    "trustTap": ["信赖触摸.wav"],
    "startup":  ["干员报到.wav"],
    "assistant":["任命助理.wav"],
    "battle":   ["作战中1.wav", "作战中2.wav", "作战中3.wav", "作战中4.wav"],
    "deploy":   ["部署1.wav", "部署2.wav"],
    "actionStart": ["行动开始.wav"],
    "actionGo": ["行动出发.wav"],
    "promote":  ["晋升后交谈1.wav", "晋升后交谈2.wav"],
    "trust":    ["信赖提升后交谈1.wav", "信赖提升后交谈2.wav", "信赖提升后交谈3.wav"],
    "elite":    ["精英化晋升1.wav", "精英化晋升2.wav"],
    "facility": ["进驻设施.wav"],
    "squad":    ["编入队伍.wav"],
    "captain":  ["任命队长.wav"],
    "fail":     ["行动失败.wav"],
    "record":   ["观看作战记录.wav"],
}

# 每条语音: (文字, 时长秒)
VOICE_META = {
    "戳一下":              ("唉？", 0.56),
    "选中干员1":           ("嗯！", 0.42),
    "选中干员2":           ("需要我的技术了吗？", 1.19),
    "问候":                ("有什么事吗？", 0.81),
    "交谈1":               ("其实我知道博士很久了哦！梅尔和缪缪她们都和我说过博士你的！我还给你带了小礼物哦！给！", 15.52),
    "交谈2":               ("这个是大帝的挂坠，就是企鹅物流的那个大帝呀，真的好可爱，每次过去都会摸上好久！", 19.35),
    "交谈3":               ("伊芙芙最近好点了吗，在我上一次离开莱茵生命的时候，她的状态有点糟糕，真的好担心……", 7.98),
    "闲置":                ("博士？博士不可以！如果睡着的话，会没命的！", 4.81),
    "信赖触摸":            ("走嘛走嘛，溜冰没那么可怕的，有我在呢。", 3.43),
    "干员报到":            ("莱茵生命科考专员麦哲伦，发现了一艘神秘的科研船？哇哇哇，你是罗德岛的博士吧，要不要加入我的探险队呢？", 14.16),
    "任命助理":            ("在下次探险之前我会一直待在你身边的，博士。有需要我的地方，请别顾虑什么，大胆地派遣我吧。", 8.16),
    "作战中1":             ("目标就位了吗？好，无人机激活！", 3.28),
    "作战中2":             ("就是现在！雪盲可是很可怕的哦！", 2.96),
    "作战中3":             ("3……2……1！", 2.14),
    "作战中4":             ("花啊！绽放吧！", 1.74),
    "部署1":               ("开始工作！", 0.83),
    "部署2":               ("设备运行良好！", 1.26),
    "行动开始":            ("无人机调试完毕，随时可以升空。", 2.57),
    "行动出发":            ("还得调试下设备……好了！", 3.74),
    "晋升后交谈1":         ("梅尔最近有造什么新东西吗，我好久没有做过新的装备，也该和她一起做些研究啦。", 16.16),
    "晋升后交谈2":         ("哼哼哼，事先说好，我可是很强的，可不要被吓到哦！", 17.06),
    "信赖提升后交谈1":     ("极北吗？那是个冰冷又残酷的梦境，但是啊，就是在那样的地方，埋藏着我的梦想。", 15.07),
    "信赖提升后交谈2":     ("小小园丁，小小花，开在屋檐下，没人照料它……这是伊芙芙以前最爱的读本。", 17.65),
    "信赖提升后交谈3":     ("极北啊……那是个既神秘又美丽的地方。博士，和我一起去吧，好吗？", 22.54),
    "精英化晋升1":         ("升级完成！现在设备的反应速度，要比之前快上一倍哦。", 4.72),
    "精英化晋升2":         ("如果博士想看看我研究的成果，我也必须要展现一下我的实力了！哼哼哼，事先说好，我可是很强的，可不要被吓到哦！", 9.96),
    "进驻设施":            ("唔？居，居然有地暖！啊~太好了~", 6.14),
    "编入队伍":            ("勘探和支援就交给我吧！", 2.08),
    "任命队长":            ("各位，要注意保持联络哦，哔哔！", 3.74),
    "行动失败":            ("被包抄了？是我的失误……", 3.73),
    "观看作战记录":        ("效率提升了呢。", 1.3),
}

# 兼容旧代码
VOICE_TEXT = {k: v[0] for k, v in VOICE_META.items()}

# 行为 -> 语音类别
BEHAVIOR_VOICES = {
    "click":       ["poke", "select", "greet", "trustTap"],
    "doubleClick": ["battle", "deploy", "actionStart"],
    "startup":     ["startup"],
    "sitDown":     ["idle", "trustTap", "record"],
    "idleChat":    ["talk", "assistant", "promote", "trust", "facility"],
    "autoWalk":    ["actionGo", "squad", "captain", "deploy"],
    "fidget":      ["poke", "select"],
    "goSleep":     ["idle"],
    "menuTalk":    ["talk", "assistant", "promote", "trustTap", "facility", "elite"],
    "menuSkill":   ["battle", "actionStart", "deploy"],
    "menuWalk":    ["actionGo", "squad", "captain"],
    "menuSit":     ["trustTap", "record"],
    "menuSleep":   ["idle"],
    "skinSwitch":  ["elite", "promote"],
    # 场景专用语音
    "sceneDroneTune": ["actionStart", "battle", "deploy"],   # 调试无人机
    "sceneLookBack":  ["talk", "assistant"],                  # 转身操作
    "sceneSpecial":   ["elite", "promote", "trust"],          # 冰霜雪特殊表演
    "sceneTale":      ["trust", "promote"],                   # 讲极北故事
    "sceneStretch":   ["trustTap", "idle"],                   # 伸懒腰
    "sceneWave":      ["greet", "select"],                    # 打招呼
    "sceneCombo":     ["actionGo", "battle"],                 # 连续点击撒娇
}


def random_voice(behavior_key):
    """按行为类别随机选：返回 (path, text, duration_seconds)"""
    keys = BEHAVIOR_VOICES.get(behavior_key, [])
    if not keys:
        return None, "", 0.0
    key = random.choice(keys)
    files = VOICES.get(key, [])
    if not files:
        return None, "", 0.0
    filename = random.choice(files)
    return _voice_from_filename(filename)


def pick_voice(filename):
    """直接指定文件名选一条语音"""
    return _voice_from_filename(filename)


def pick_voice_from(pool):
    """从文件名池随机选一条"""
    if not pool:
        return None, "", 0.0
    return _voice_from_filename(random.choice(pool))


def _voice_from_filename(filename):
    path = os.path.join(ASSETS, "voices", filename)
    stem = filename.replace(".wav", "")
    text, dur = VOICE_META.get(stem, ("", 0.0))
    return path, text, dur
