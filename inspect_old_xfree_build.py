from pathlib import Path

p = Path(r"C:\Users\SM.DESKTOP-P1R0508.000\Desktop\DESKTOP\StremioPowerSetup\xfree-hq\xfree_build.py")
if p.exists():
    lines = p.read_text(encoding="utf-8", errors="ignore").split("\n")
    for i, line in enumerate(lines[:80]):
        print(f"{i+1}: {line}")
else:
    print("File not found")
