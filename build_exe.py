# Python · build_exe.py · Plaza Wallet · Windows · Python 3.10+ / PyInstaller
"""Build a standalone Windows EXE. Install requirements-build.txt first."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def build(distpath, workpath):
    if sys.platform != "win32":
        raise RuntimeError("Build the Windows executable on Windows.")
    distpath, workpath = Path(distpath).resolve(), Path(workpath).resolve()
    distpath.mkdir(parents=True, exist_ok=True)
    workpath.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--onefile", "--windowed",
        "--noupx", "--name", "PlazaWallet", "--distpath", str(distpath),
        "--workpath", str(workpath / "cache"), "--specpath", str(workpath),
        "--add-data", str(ROOT / "zz_plaza_wallet.rpy") + ";.",
        str(ROOT / "plaza_wallet.py"),
    ], check=True, cwd=ROOT)
    return distpath / "PlazaWallet.exe"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--distpath", type=Path, default=ROOT / "dist")
    parser.add_argument("--workpath", type=Path, default=ROOT / "build")
    args = parser.parse_args()
    print(build(args.distpath, args.workpath))
