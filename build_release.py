# Python · build_release.py · Plaza Wallet · Windows · Python 3.10+
"""Build a source ZIP using an allowlist, excluding personal settings and saves."""
import argparse
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
FILES = (
    ".gitattributes", ".gitignore", "README.md", "LEIA-ME.md", "LEEME.md",
    "Start.bat", "Iniciar.bat", "plaza_wallet.py", "i18n.py",
    "zz_plaza_wallet.rpy", "settings.example.json",
    "test_plaza_wallet.py", "test_i18n.py", "build_release.py",
    "build_exe.py", "executable_check.py", "requirements-build.txt",
)


def build(destination):
    destination = Path(destination).resolve()
    if destination.suffix.lower() != ".zip":
        raise ValueError("The output must be a .zip file.")
    for name in FILES:
        if not (ROOT / name).is_file():
            raise FileNotFoundError(name)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            archive.write(ROOT / name, "PlazaWallet/" + name)
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("ZIP verification failed.")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "PlazaWallet.zip")
    args = parser.parse_args()
    print(build(args.output))
