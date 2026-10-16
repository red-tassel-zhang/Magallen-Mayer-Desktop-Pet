"""麦哲伦桌面宠物 —— PyInstaller 打包脚本

用法: python build.py
产物: dist/麦哲伦.exe (单文件, ~200MB 含所有 webm/wav)

依赖: pip install pyinstaller pillow
"""
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
NAME = "麦哲伦"
ICON_PNG = os.path.join(BASE, "立绘_麦哲伦_2.png")
ICON_ICO = os.path.join(BASE, "app.ico")


def make_ico():
    """把 PNG 转成多尺寸 ICO 供 Windows exe 用"""
    try:
        from PIL import Image
    except ImportError:
        print("[!] Pillow 未安装，跳过 .ico 生成 (pip install pillow)")
        return None
    if not os.path.exists(ICON_PNG):
        print(f"[!] 立绘不存在: {ICON_PNG}")
        return None
    img = Image.open(ICON_PNG).convert("RGBA")
    # 裁到接近正方形（保头）
    w, h = img.size
    side = min(w, h)
    # 从上方偏中间裁（保留头部）
    left = (w - side) // 2
    top = 0
    img = img.crop((left, top, left + side, top + side))
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(ICON_ICO, format="ICO", sizes=sizes)
    print(f"[+] 已生成 {ICON_ICO}")
    return ICON_ICO


def clean():
    for d in ("build", "dist", "__pycache__"):
        p = os.path.join(BASE, d)
        if os.path.exists(p):
            shutil.rmtree(p, ignore_errors=True)
    spec = os.path.join(BASE, f"{NAME}.spec")
    if os.path.exists(spec):
        os.remove(spec)


def build():
    ico = make_ico()

    # --add-data 在 Windows 上用 ";", Linux/Mac 用 ":"
    sep = ";" if sys.platform == "win32" else ":"

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", NAME,
        f"--add-data=assets{sep}assets",
        f"--add-data=bbb{sep}bbb",
        f"--add-data=立绘_麦哲伦_2.png{sep}.",
        # 精简：不带 test / cv2 examples
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "pandas",
        "--exclude-module", "notebook",
        "--exclude-module", "IPython",
    ]
    if ico and os.path.exists(ico):
        args += ["--icon", ico]

    args.append("main.py")

    print("[+] 运行 PyInstaller:")
    print("    " + " ".join(args))
    subprocess.run(args, cwd=BASE, check=True)

    exe = os.path.join(BASE, "dist", f"{NAME}.exe")
    if os.path.exists(exe):
        size_mb = os.path.getsize(exe) / 1024 / 1024
        print(f"\n[OK] build succeeded: {exe} ({size_mb:.1f} MB)")
    else:
        print("\n[FAIL] no exe in dist/")


if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
        print("[+] 已清理 build/ dist/ *.spec")
        sys.exit(0)
    clean()
    build()
