<div align="center">

# 麦哲伦 & 梅尔 · 桌宠

**明日方舟** 角色桌面宠物 —— 用 Python + PySide6 写的两个 Windows 桌宠

莱茵生命科考专员 **麦哲伦** &nbsp;·&nbsp; 机械发明家 **梅尔**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.5%2B-41CD52?logo=qt&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

🎂 &nbsp;**10 月 17 日是麦哲伦的生日 —— 生日快乐！**&nbsp; 🎂

</div>

---

## 📖 这是什么

两个互不干扰、可以同时运行的桌面宠物，都基于同一套渲染内核：

- **`main.py`** —— 麦哲伦（Magallan），带双皮肤和龙腾无人机
- **`main_mayer.py`** —— 梅尔（Mayer），带双皮肤和机械水獭「咪波」

角色会待在你的桌面上自己发呆、走动、坐下、睡觉，被戳会有反应，
并且**透明区域的鼠标点击会穿透到桌面**——不会挡住你干活。

## ✨ 功能特性

| | 麦哲伦 | 梅尔 |
|---|---|---|
| **皮肤** | 默认 / 回味冰霜雪 | 默认 / 庭院寻梦尖兵 |
| **搭档** | 龙腾无人机 A / F / L 三型，空中浮动 | 机械水獭「咪波」，贴地跟在脚边 |
| **中文语音** | 37 条 | 37 条 |
| **特殊动作** | 冰霜雪皮肤 `Special` 动画 | 庭院皮肤专属 `Special` |
| **背面动画** | ✅ 4 个 | — |
| **行为系统** | 场景调度（闲置 / 走动 / 坐下 / 睡觉 / 小动作） | 行为树 20 个场景 + 情绪引擎 |

**两者共有：**

- 🖱️ **点击穿透** —— `WM_NCHITTEST` 系统级实现，透明像素自动穿透到桌面
- ✋ **拖拽移动** —— 按住角色任意位置就能拖走
- 💬 **对话气泡** —— 打字机效果，自动定位在角色头顶并左右避让
- 🎤 **语音播放** —— `QSoundEffect` 播放，异常时自动回退到 `winsound`
- 🗂️ **右键菜单** —— 说话 / 放搭档 / 走一走 / 坐下 / 睡觉 / 换装 / 隐藏 / 退出
- 📌 **系统托盘** —— 左键显示隐藏，右键快捷操作
- 🎬 **绿幕抠图** —— OpenCV 解码 WebM + numpy 向量化色度键去背景
- ⚡ **循环动画帧缓存** —— 首轮预计算，后续零开销（96 MB 预算封顶）

## 🚀 快速开始

```bash
# 1. 安装依赖
pip install PySide6 opencv-python numpy

# 2. 运行麦哲伦
python main.py

# 3. 运行梅尔（可以同时开）
python main_mayer.py
```

> **注意**：请使用**系统 Python** 运行，不要用 PyCharm 自带的 venv——
> 项目依赖已装在全局环境。

也可以直接从 [Releases](https://github.com/red-tassel-zhang/Magallen-Mayer-Desktop-Pet/releases)
下载打包好的 `麦哲伦.exe` / `梅尔.exe`，双击即用，不需要装 Python。

## 📁 目录结构

```
.
├── main.py                    # 麦哲伦 入口：托盘图标 + 对话气泡
├── pet_window.py              # 麦哲伦 主窗口：渲染 / 交互 / 闲置行为 / 点击穿透
├── data.py                    # 麦哲伦 资源路径映射 + 37 条语音台词
├── behavior.py                # 麦哲伦 行为调度
├── build.py                   # 麦哲伦 PyInstaller 打包脚本
│
├── main_mayer.py              # 梅尔 入口
├── pet_window_mayer.py        # 梅尔 主窗口（含咪波定位）
├── data_mayer.py              # 梅尔 资源映射 + 台词
├── behavior_mayer.py          # 梅尔 行为树 + 情绪引擎
├── build_mayer.py             # 梅尔 打包脚本
│
├── animation_player.py        # [共用] WebM 解码 + 色度键抠图 + 帧缓存
├── voice_player.py            # [共用] WAV 语音播放
│
├── assets/                    # 麦哲伦 素材
│   ├── default/               #   默认皮肤 17 个 webm
│   ├── frosty/                #   回味冰霜雪皮肤 16 个 webm
│   ├── drones/{A,F,L}/        #   龙腾无人机 28 个 webm
│   └── voices/                #   38 个中文语音 wav
├── bbb/                       # 麦哲伦 绿幕素材（抠图用）52 个 webm
├── mayer/                     # 梅尔 素材：动画 + 语音 + 立绘
│
├── main.js / preload.js       # Electron 早期原型（仅麦哲伦，实验性）
├── renderer/                  # ↑ 原型的渲染层
└── docs/                      # PROJECT.md / MAYER.md 开发笔记
```

## 🎛 手动调参

调整手感时最常用的几个位置：

| 参数 | 位置 | 说明 |
|------|------|------|
| 绿幕阈值（全透） | `animation_player.py:81` | `green_strength >= 80`，调小 = 更激进去绿边 |
| 绿幕羽化区间 | `animation_player.py:82-83` | `30 ~ 80`，调小 = 羽化更宽、边缘更柔 |
| 绿幕触发目录 | `animation_player.py:39` | `("bbb", "mayer")` |
| 帧缓存上限 | `animation_player.py:9` | `MAX_CACHE_BYTES = 96 MB` |
| 渲染缩放上限 | `animation_player.py:10` | `MAX_FRAME_DIM = 560` |
| 麦哲伦窗口尺寸 | `pet_window.py` | 默认 `500 × 650` |
| 梅尔窗口尺寸 | `pet_window_mayer.py:35` | `500 × 650` |
| 咪波缩放 | `pet_window_mayer.py:262` | `ds = 0.5` |
| 咪波 Y 偏移 | `pet_window_mayer.py:219` | 在 `base_y` 公式末尾加减像素 |

## 📦 打包成 exe

```bash
pip install pyinstaller

python build.py          # 产出 dist/麦哲伦.exe
python build_mayer.py    # 产出 dist/梅尔.exe，并自动生成 mayer_app.ico
```

打包脚本会自动把素材目录塞进单文件 exe，并处理 `_MEIPASS` 相对路径问题。
单文件 exe 体积约 **160 ~ 190 MB**（主要是 webm 动画）。

## 🧩 技术要点

**为什么不用透明窗口 + PNG 序列？**
原画是带背景的 WebM 视频。项目用两套色度键策略把它变成带 Alpha 的 RGBA：

- **绿幕素材**（`bbb/`、`mayer/`）：走快速通道，
  `green_strength = G - (R + B) / 2`，比逐像素欧氏距离快一个数量级；
- **黑底素材**（`assets/`）：采样四角背景色的中位亮度作为基准色，
  再按 RGB 距离做软阈值。

**点击穿透**用 Win32 的 `WM_NCHITTEST` 原生实现，而不是 Qt 的
`WA_TransparentForMouseEvents`——只有当前 alpha 为 0 的像素才返回 `HTTRANSPARENT`，
所以角色身上的像素依然可以拖拽。

## ⚠️ 已知问题

- 冰霜雪皮肤的 `正面-Skill` 动画缺失，双击时会 fallback 到默认皮肤
- `QSoundEffect` 对部分 wav 格式不兼容（已回退 `winsound`）
- 屏幕边界检测比较简陋，角色走太远可能出屏
- `renderer/` 里的 Electron 原型缺 `renderer/icon.png`，托盘图标会被跳过

## 📜 版权与许可

- **代码**：MIT License，见 [LICENSE](LICENSE)
- **游戏素材**（`assets/` `bbb/` `mayer/` `renderer/assets/` 立绘等）：
  著作权归 **上海鹰角网络（Hypergryph）** 所有，仅限学习与个人非商业用途，
  **不在 MIT 协议覆盖范围内**。详见 [NOTICE.md](NOTICE.md)

本项目是非官方粉丝作品，与上海鹰角网络无隶属关系。

---

<div align="center">

如果这个项目让你会心一笑，欢迎点个 ⭐ Star

**祝麦哲伦 10 月 17 日生日快乐 🎂**

</div>
