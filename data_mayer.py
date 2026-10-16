"""梅尔桌面宠物 —— 资源路径映射 & 语音文字数据"""
import os
import random
import sys

BASE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, "mayer")

# ========== 皮肤动画路径 ==========
def _anim_path(skin, name):
    return os.path.join(ASSETS, f"梅尔-{_SKIN_PREFIX[skin]}-{name}-x1.webm")

_SKIN_PREFIX = {
    "default": "默认",
    "garden": "庭院寻梦尖兵",
}

_ANIM_MAP = {
    "relax":    "基建-Relax",
    "interact": "基建-Interact",
    "move":     "基建-Move",
    "sit":      "基建-Sit",
    "sleep":    "基建-Sleep",
    "special":  "基建-Special",   # 仅庭院寻梦尖兵有
    "start":    "正面-Start",
    "idle":     "正面-Idle",
    "skill":    "正面-Skill",
    "attack":   "正面-Attack",
    "die":      "正面-Die",
}

ANIM_LOOP = {
    "relax", "move", "idle", "sleep", "sit",
}

def get_anim_path(skin, anim_name):
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
    """梅尔没有绿幕素材，直接返回 None"""
    return None


# ========== 无人机动画路径 ==========
DRONE_TYPES = ["otter"]  # 机械水獭只有一种型号

def get_drone_path(skin, drone_type, anim_name):
    prefix = _SKIN_PREFIX.get(skin, "默认")
    filename = f"机械水獭-{prefix}-战斗-{anim_name}-x1.webm"
    path = os.path.join(ASSETS, filename)
    if not os.path.exists(path) or os.path.getsize(path) < 500:
        filename = f"机械水獭-默认-战斗-{anim_name}-x1.webm"
        path = os.path.join(ASSETS, filename)
        if not os.path.exists(path) or os.path.getsize(path) < 500:
            return None
    return path


def get_green_drone_path(skin, drone_type, anim_name):
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

VOICE_META = {
    "戳一下":              ("呜哇！我还在工作中啊！", 2.39),
    "选中干员1":           ("呜哇！", 0.61),
    "选中干员2":           ("小心，小心一点！", 1.99),
    "问候":                ("博士！你好！", 1.82),
    "交谈1":               ("工程部的人每次都不认可我的提案，是不是不喜欢我啊，怎么办……对了博士，你去代我提交下这份改进意见吧！就这么定了！", 13.81),
    "交谈2":               ("莱茵生命里像我这样的工作室还有很多啦，但别的工作室三周才能完成一半的任务，我一周就能搞定。这可不是在吹牛哦。", 14.97),
    "交谈3":               ("我做研究的时候千万别打扰我，我是会让咪波咬你的！我自己也会！", 6.36),
    "闲置":                ("哈啊……咖啡机在哪里……呼，博士你也要来点儿吗？", 8.67),
    "信赖触摸":            ("博士，让我摸摸你的头，会很有灵感的！", 5.16),
    "干员报到":            ("莱茵生命所属，鲁特拉工作室，竭诚为您服务。是的，没有其他成员，我一人就是整个工作室。很厉害吧！", 12.60),
    "任命助理":            ("建筑设计，工业研发，科学研究，只要博士想得到的，我都能做到。", 6.53),
    "作战中1":             ("去吧，咪波三号！", 2.16),
    "作战中2":             ("咪波，咬他！", 2.05),
    "作战中3":             ("身体破损的话，再造一个就好了！", 3.06),
    "作战中4":             ("我的咪波们可不仅仅是机械那么简单！", 3.55),
    "部署1":               ("轻拿轻放！", 1.47),
    "部署2":               ("精密仪器是很贵重的！", 2.29),
    "行动开始":            ("上吧咪波，给敌人看看我们莱茵生命的技术力！", 5.45),
    "行动出发":            ("这次也能得到良好的实验数据吧！", 2.85),
    "晋升后交谈1":         ("晚上总是会很有灵感呢……但又……非常困！不，不行了，枕头在哪……我要休息一下……", 12.89),
    "晋升后交谈2":         ("嗯？你想问为什么它们叫咪波？咪波是它的启动音效嘛，我觉得挺合适的。不像？那你可以摁下这个开关——等等！不是那个！那是自毁———呜啊啊啊，快跑！！", 20.08),
    "信赖提升后交谈1":     ("刚刚走过去的……是赫默吧。如果那时候……喔，抱歉，保密协议还没过期，我不该多嘴的。", 12.07),
    "信赖提升后交谈2":     ("闲下来就只会感到空虚呢……工程师就是这样的人啦。博士也会无所事事吗？不会？", 10.31),
    "信赖提升后交谈3":     ("博士，我能申请——不是！不用十平米！上次是我不对，这回——三平米就够了！别，别跑啊博士！一平米实用科研面积也行！求你了！", 15.43),
    "精英化晋升1":         ("这次涨薪可真是及时，我又能升级一下设备了。", 4.83),
    "精英化晋升2":         ("我向您保证过一定能出成果，现在，怎么样，是不是很令人满意呀~", 7.25),
    "进驻设施":            ("我想要个新的工作室了！", 2.34),
    "编入队伍":            ("咪波们，该上场咯！", 1.90),
    "任命队长":            ("要同时指挥大家和咪波，就算是我也有点手忙脚乱……！", 5.87),
    "行动失败":            ("不！咪波——！……只，只能再造几台身体了……", 6.79),
    "观看作战记录":        ("这个结构——有些意思，我得研究一下。", 4.30),
}

VOICE_TEXT = {k: v[0] for k, v in VOICE_META.items()}

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
    "sceneDroneTune": ["actionStart", "battle", "deploy"],
    "sceneLookBack":  ["talk", "assistant"],
    "sceneSpecial":   ["elite", "promote", "trust"],
    "sceneTale":      ["trust", "promote"],
    "sceneStretch":   ["trustTap", "idle"],
    "sceneWave":      ["greet", "select"],
    "sceneCombo":     ["actionGo", "battle"],
}


def random_voice(behavior_key):
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
    return _voice_from_filename(filename)


def pick_voice_from(pool):
    if not pool:
        return None, "", 0.0
    return _voice_from_filename(random.choice(pool))


def _voice_from_filename(filename):
    path = os.path.join(ASSETS, filename)
    stem = filename.replace(".wav", "")
    text, dur = VOICE_META.get(stem, ("", 0.0))
    return path, text, dur
