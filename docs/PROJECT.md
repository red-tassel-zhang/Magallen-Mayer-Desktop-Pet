# 麦哲伦桌面宠物 - 项目状态

## 技术栈
- **Python 3.14** + **PySide6** + **OpenCV** + **numpy**
- 运行命令：`python main.py`（用系统 Python，不是 PyCharm venv）
- 依赖：`pip install PySide6 opencv-python numpy`

## 文件结构
```
desktop_pet/
├── main.py                 # 入口 + 对话气泡窗口 + 右键菜单连接
├── pet_window.py           # 主窗口：渲染、交互、动画控制、闲置行为、WM_NCHITTEST点击穿透
├── animation_player.py     # OpenCV解码webm + numpy色度键去背景 + 循环动画帧缓存
├── voice_player.py         # QSoundEffect播放wav语音
├── data.py                 # 资源路径映射（双皮肤+无人机+38条语音）
├── requirements.txt
└── assets/
    ├── default/            # 默认皮肤 17个webm（基建Relax/Move/Interact/Sit/Sleep + 正面/背面）
    ├── frosty/             # 冰霜雪皮肤 16个webm（含Special特殊动画5.6M）
    ├── drones/{A,F,L}/     # 龙腾无人机 共33个webm（3型 x 2皮肤）
    └── voices/             # 38个wav中文语音
```

## 已实现功能

### 动画
| 触发 | 动画 | 说明 |
|------|------|------|
| 出场 | start → relax | 正面Start播放后切基建Relax |
| 闲置 | relax / idle / backIdle | 每25~55s随机切换姿态 |
| 单击 | interact → relax | 被戳互动 |
| 双击 | skill → relax + 无人机 | 放出3台龙腾无人机4秒 |
| 小动作 | interact → relax | 每15~35s自动触发，30%概率带语音 |
| 自主走动 | move + 位移 | 每45~90s走3~7秒，屏幕边界反弹 |
| 30s无操作 | sit | 坐下 |
| 2min无操作 | interact + 语音 | 随机交谈 |
| 5min无操作 | sleep | 睡觉 |
| 退出 | die | 退场动画 |

### 交互
- **拖拽**：鼠标拖拽移动窗口
- **点击穿透**：WM_NCHITTEST 系统级，透明像素自动穿透到桌面
- **右键菜单**：说话、放无人机、走一走、坐下、睡觉、换装、隐藏、退出
- **换装**：默认 ↔ 冰霜雪皮肤切换（含语音）
- **无人机**：双击或右键触发，3台龙腾A/F/L同时出现，自动匹配当前皮肤

### 语音
- 38条wav中文语音（麦哲伦为中文配音，梅尔为日文配音）
- 每个交互随机从对应类别选取
- 对话气泡打字效果，动态定位在角色头顶

### 性能
- 循环动画帧缓存：首轮预计算色度键，后续零开销
- 渲染间隔50ms（20fps）
- 色度键：numpy向量化，采样四角背景色 + RGB距离判断

## 已知问题
- 冰霜雪皮肤的 `正面-Skill` 动画不存在，双击时用默认skin fallback
- 语音播放用QSoundEffect，部分wav格式可能不兼容（回退到winsound）
- 屏幕边界检测较简陋，走太远可能出屏

## 打包为exe
```
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```
需要处理相对路径问题（`__file__` 在打包后指向临时目录）。

## 下次继续的方向
- [ ] 更多动画绑定（Special特殊动画、Attack、backAttack等）
- [ ] 文字对话输入交互（打字和麦哲伦聊天）
- [ ] 系统托盘图标
- [ ] 窗口大小自适应角色
- [ ] PyInstaller打包配置
- [ ] 定时提醒/闹钟功能
- [ ] 情感状态系统（好感度变化影响行为和台词）
