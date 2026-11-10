# Python · test_i18n.py · Plaza Wallet · Windows · Python 3.10+ / unittest
import ast
import json
from pathlib import Path
import string
import tempfile
import time
import unittest
from unittest.mock import patch
import i18n
import plaza_wallet as app


class TranslationTests(unittest.TestCase):
    def test_catalogs_and_placeholders_are_complete(self):
        formatter = string.Formatter()
        source = i18n.CATALOGS["pt-BR"]
        self.assertEqual(len(source), len(i18n.ROWS))
        for language, catalog in i18n.CATALOGS.items():
            self.assertEqual(set(catalog), set(source), language)
            for key, translated in catalog.items():
                expected = {name for _, name, _, _ in formatter.parse(key) if name}
                actual = {name for _, name, _, _ in formatter.parse(translated) if name}
                self.assertEqual(expected, actual, (language, key))
                self.assertTrue(translated.strip())

    def test_all_literal_ui_keys_have_translations(self):
        tree = ast.parse((app.BASE / "plaza_wallet.py").read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "tr":
                if node.args and isinstance(node.args[0], ast.Constant):
                    self.assertIn(node.args[0].value, i18n.CATALOGS["en"])

    def test_locale_numbers_and_unknown_language(self):
        self.assertEqual(i18n.number("en", 3000), "3,000")
        self.assertEqual(i18n.number("pt-BR", 3000.5), "3.000,50")
        self.assertEqual(i18n.number("es", 3000.5), "3.000,50")
        self.assertEqual(i18n.translate("unknown", "Continuar"), "Continue")
        self.assertEqual(i18n.translate("en", "Conector removido. Cópia guardada em {path}", path="C:/test"),
                         "Connector removed. Backup saved to C:/test")

    def test_frozen_preferences_use_executable_directory(self):
        executable = Path(__file__).resolve().parent / "fake-exe-folder" / "PlazaWallet.exe"
        with patch.object(app.sys, "frozen", True, create=True), patch.object(app.sys, "executable", str(executable)):
            self.assertEqual(app.application_directory(), executable.parent)
        self.assertEqual(app.application_directory(), app.BASE)


class LanguageUITests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.window = None

    def tearDown(self):
        if self.window is not None:
            for job in self.window.tk.call("after", "info"):
                self.window.after_cancel(job)
            self.window.destroy()
        self.temp.cleanup()

    def open(self, language=None):
        self.window = app.Wallet(language=language, settings_path=self.root / "settings.local.json")
        self.window.update()
        return self.window

    def test_startup_picker_switch_and_persistence(self):
        window = self.open()
        self.assertFalse(window._started)
        for language, continue_text in (("en", "Continue"), ("es", "Continuar"), ("pt-BR", "Continuar")):
            window.language_choice.set(language)
            window.preview_language()
            self.assertEqual(window.continue_button.cget("text"), continue_text)
        window.language_choice.set("en")
        window.preview_language()
        window.continue_button.invoke()
        window.update()
        self.assertTrue(window._started)
        self.assertEqual(window.scan_button.cget("text"), "Read game")
        self.assertEqual(app.load_settings(window.settings_path)["language"], "en")
        window.show_language_picker()
        window.language_choice.set("es")
        window.preview_language()
        window.start_wallet()
        window.update()
        self.assertEqual(window.scan_button.cget("text"), "Leer juego")
        self.assertEqual(app.load_settings(window.settings_path)["language"], "es")

    def test_live_status_error_and_enable_survive_translation(self):
        window = self.open("en")
        game = self.root / "game"
        folder = game / "plaza_wallet"
        folder.mkdir(parents=True)
        window.game = game
        response = {"protocol": 1, "time": time.time(), "entries": [
            {"path": ["money"], "name": "money", "value": 3000}],
            "id": "test", "enabled": True, "path": ["money"], "current": 3000, "error": ""}
        file = folder / "response.json"
        file.write_text(json.dumps(response))
        window.poll()
        self.assertEqual(window.status.get(), "●  Game connected")
        self.assertEqual(window.mode_text.get(), "REFILL ACTIVE")
        self.assertEqual(window.balance_text.get(), "3,000")
        window.show_language_picker()
        window.language_choice.set("es")
        window.preview_language()
        window.start_wallet()
        window.poll()
        self.assertEqual(window.mode_text.get(), "RECARGA ACTIVA")
        self.assertEqual(window.balance_text.get(), "3.000")
        self.assertEqual(window.entries[0]["path"], ["money"])
        response["error"] = "Carregue uma partida antes de ativar."
        file.write_text(json.dumps(response))
        window.poll()
        self.assertEqual(window.details.get(), "Carga una partida antes de activar la recarga.")
        with patch.object(app, "write_command", return_value="command-id") as send:
            window.enable()
            send.assert_called_once_with(game, "enable", path=["money"], amount=3000)

    def test_invalid_settings_and_translated_dialog(self):
        (self.root / "settings.local.json").write_text("not json")
        window = self.open("en")
        self.assertIsNone(window.game)
        with patch.object(app.filedialog, "askdirectory", return_value=str(self.root)), \
             patch.object(app.messagebox, "showerror") as error:
            window.choose()
            self.assertEqual(error.call_args.args[0], "Invalid folder")
            self.assertIn("Select the Ren'Py game folder", error.call_args.args[1])

    def test_saved_language_is_preselected_on_next_launch(self):
        app.save_settings(self.root / "settings.local.json", {"language": "es", "game_path": "", "amount": 3000})
        window = self.open()
        self.assertFalse(window._started)
        self.assertEqual(window.language_choice.get(), "es")
        self.assertEqual(window.picker_title.cget("text"), "Elige tu idioma")
        window.poll()
        self.assertFalse(window._started)

    def test_malformed_language_falls_back_to_english(self):
        app.save_settings(self.root / "settings.local.json", {"language": [], "game_path": ""})
        window = self.open()
        self.assertEqual(window.language_choice.get(), "en")


if __name__ == "__main__":
    unittest.main(verbosity=2)
