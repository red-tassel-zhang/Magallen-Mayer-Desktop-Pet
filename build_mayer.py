"""梅尔桌面宠物 —— PyInstaller 打包脚本

用法: python build_mayer.py
产物: dist/梅尔.exe (单文件)
"""
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
NAME = "梅尔"
ICON_PNG = os.path.join(BASE, "mayer", "立绘_梅尔_skin1.png")
ICON_ICO = os.path.join(BASE, "mayer_app.ico")


def make_ico():
    try:
        from PIL import Image
    except ImportError:
        print("[!] Pillow 未安装，跳过 .ico 生成 (pip install pillow)")
        return None
    if not os.path.exists(ICON_PNG):
        print(f"[!] 立绘不存在: {ICON_PNG}")
        return None
    img = Image.open(ICON_PNG).convert("RGBA")
    w, h = img.size
    side = min(w, h)
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


def build():
    ico = make_ico()

    sep = ";" if sys.platform == "win32" else ":"

    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", NAME,
        f"--add-data=mayer{sep}mayer",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "pandas",
        "--exclude-module", "notebook",
        "--exclude-module", "IPython",
    ]
    if ico and os.path.exists(ico):
        args += ["--icon", ico]

    args.append("main_mayer.py")

    print("[+] 运行 PyInstaller:")
    print("    " + " ".join(args))
    subprocess.run(args, cwd=BASE, check=True)

    exe = os.path.join(BASE, "dist", f"{NAME}.exe")
    if os.path.exists(exe):
        size_mb = os.path.getsize(exe) / 1024 / 1024
        print(f"\n[OK] 打包成功: {exe} ({size_mb:.1f} MB)")
    else:
        print("\n[FAIL] dist/ 中没有 exe")


if __name__ == "__main__":
    if "--clean" in sys.argv:
        clean()
        print("[+] 已清理 build/ dist/")
        sys.exit(0)
    clean()
    build()
