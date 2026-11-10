# Python · executable_check.py · Plaza Wallet · Windows · Python 3.10+
"""A diagnostic for the built executable, using only an isolated fake game."""
import json
from pathlib import Path
import sys
import tempfile
import traceback
from i18n import LANGUAGES


def run(report_path, wallet_class, installer, bridge_resource):
    report_path = Path(report_path).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    result = {"passed": False, "frozen": bool(getattr(sys, "frozen", False)), "checks": []}
    window = None
    try:
        with tempfile.TemporaryDirectory(prefix="plaza-check-", dir=report_path.parent) as scratch:
            root = Path(scratch)
            game = root / "fake-game" / "game"
            game.mkdir(parents=True)
            (game.parent / "renpy").mkdir()
            installer(game)
            assert (game / bridge_resource.name).read_bytes() == bridge_resource.read_bytes()
            result["checks"].append("bundled connector installation")
            settings = root / "settings.local.json"
            window = wallet_class(settings_path=settings)
            window.update()
            assert not window._started
            result["checks"].append("startup language picker")
            for language in LANGUAGES:
                window.show_language_picker()
                window.language_choice.set(language)
                window.preview_language()
                window.start_wallet()
                window.update()
                assert window.scan_button.cget("text") == window.tr("Ler jogo")
                assert json.loads(settings.read_text(encoding="utf-8"))["language"] == language
                assert window.game is None
                result["checks"].append("interface and settings: " + language)
            for job in window.tk.call("after", "info"):
                window.after_cancel(job)
            window.destroy()
            window = None
            result["passed"] = True
    except Exception:
        result["error"] = traceback.format_exc()
    finally:
        if window is not None:
            try:
                window.destroy()
            except Exception:
                pass
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result["passed"] else 1
