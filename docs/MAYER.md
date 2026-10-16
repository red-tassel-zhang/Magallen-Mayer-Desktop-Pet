# 梅尔桌面宠物

明日方舟干员 **梅尔（Mayer）** 的 PySide6 桌面宠物。

## 运行

```bash
# 源码运行
python main_mayer.py

# 或直接双击打包好的 exe
dist/梅尔.exe
```

依赖：`PySide6 opencv-python numpy`

## 文件结构

```
desktop_pet/
├── main_mayer.py          # 入口：托盘图标、对话气泡
├── data_mayer.py          # 资产路径映射、37条语音台词和时长
├── behavior_mayer.py      # 行为树：情绪系统 + 20个场景
├── pet_window_mayer.py    # 透明窗口：动画渲染、咪波、皮肤切换
├── build_mayer.py         # PyInstaller 打包脚本
│
├── animation_player.py    # [共用] WebM 解码 + 色度键绿幕抠图
├── voice_player.py        # [共用] WAV 语音播放
│
└── mayer/                 # 梅尔素材目录
    ├── 梅尔-默认-*.webm         # 默认皮肤动画 (10个)
    ├── 梅尔-庭院寻梦尖兵-*.webm # 庭院寻梦尖兵皮肤动画 (11个)
    ├── 机械水獭-*-战斗-*.webm   # 咪波动画 (10个)
    ├── *.wav                    # 中文配音 (37条)
    └── 立绘_梅尔_skin1.png      # 立绘 (托盘图标)
```

## 功能

- **双皮肤**：默认 / 庭院寻梦尖兵（右键菜单换装）
- **咪波（机械水獭）**：1只地面机械狗，位置根据角色包围盒动态定位到脚边
- **特殊动作**：庭院寻梦尖兵皮肤专属（`special` 动画），右键菜单仅在装备该皮肤时显示
- **37条中文配音**：含气泡字幕打字机效果，台词原文来自游戏
- **行为树**：20个场景，情绪引擎（energy/social/curiosity）自动调度动作
- **点击穿透**：透明区域不响应鼠标，可拖拽移动
- **系统托盘**：左键显隐，右键说句话/放出咪波/退出

## 打包

```bash
python build_mayer.py
```

产物：`dist/梅尔.exe` (~164MB 单文件)

打包脚本会自动：
1. 从 `mayer/立绘_梅尔_skin1.png` 生成 `mayer_app.ico`
2. 将 `mayer/` 整个目录打包进 exe
3. 使用 `--windowed` 无控制台窗口

## 手动调参

位置/渲染相关参数都在以下文件中，方便调整：

| 参数 | 文件:行 | 说明 |
|------|---------|------|
| **咪波 Y 偏移** | `pet_window_mayer.py:219` | 在 `base_y` 公式末尾加减像素 |
| **咪波缩放** | `pet_window_mayer.py:262` | `ds = 0.5` |
| **绿幕阈值(全透)** | `animation_player.py:74` | `>= 80`，改小 = 更激进去绿边 |
| **绿幕阈值(羽化)** | `animation_player.py:75` | `30 ~ 80`，改小 = 羽化区更宽 |
| **绿幕触发目录** | `animation_player.py:38` | `("bbb", "mayer")` |
| **窗口尺寸** | `pet_window_mayer.py:35` | `500, 650` |
| **咪波出现时长** | `pet_window_mayer.py:103` | `duration=4000` (ms) |

## 与麦哲伦的差异

| | 麦哲伦 | 梅尔 |
|---|--------|------|
| 入口 | `main.py` | `main_mayer.py` |
| 皮肤 | default / frosty (回味冰霜雪) | default / garden (庭院寻梦尖兵) |
| 无人机 | 1-3台 龙腾(A/F/L)，空中浮动 | 1只 机械水獭，地面脚边 |
| 绿幕素材 | bbb/ 目录 | 无，直接用 mayer/ 做色度键 |
| 素材目录 | assets/ + bbb/ | mayer/ |
| 背面动画 | 有 (4个) | 无 |
