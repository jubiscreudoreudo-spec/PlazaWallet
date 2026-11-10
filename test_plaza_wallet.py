# Python · test_plaza_wallet.py · Plaza Wallet · Windows · Python 3.10+ / unittest
import json
from pathlib import Path
import sys
import tempfile
import textwrap
import time
import types
import unittest
from unittest.mock import patch

import plaza_wallet as app


class RenpyList(list):
    pass


class RenpyDict(dict):
    pass


class WalletTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.game = self.root / "game"
        self.game.mkdir()
        (self.root / "renpy").mkdir()
        self.store = types.SimpleNamespace(money=150, energy=8, flag=True,
                                          player=types.SimpleNamespace(cash=65.5),
                                          inventory={"wallet": 17}, main_menu=False)
        self.engine = types.ModuleType("renpy")
        self.engine.config = types.SimpleNamespace(gamedir=str(self.game), name="Test fixture", version="1",
                                                 interact_callbacks=[], python_callbacks=[], periodic_callbacks=[])
        self.engine.store = self.store
        self.engine.log = lambda message: None
        source = (app.BASE / app.BRIDGE).read_text(encoding="utf-8")
        body = textwrap.dedent(source.split("init 999 python hide:\n", 1)[1])
        hidden_locals = {}
        with patch.dict(sys.modules, {"renpy": self.engine}):
            exec(compile(body, app.BRIDGE, "exec"), {"list": RenpyList, "dict": RenpyDict}, hidden_locals)
        self.namespace = hidden_locals["_plaza_wallet_context"]

    def tearDown(self):
        self.temp.cleanup()

    def poll(self):
        self.namespace["state"]["last_poll"] = 0
        self.namespace["poll"]()
        return json.loads((self.game / "plaza_wallet" / "response.json").read_text())

    def command(self, action, **params):
        identity = app.write_command(self.game, action, **params)
        result = self.poll()
        self.assertEqual(identity, result["id"])
        return result

    def test_scan_does_not_modify_values(self):
        result = self.command("scan")
        values = {item["name"]: item["value"] for item in result["entries"]}
        self.assertEqual(values["money"], 150)
        self.assertEqual(values["player.cash"], 65.5)
        self.assertEqual(values["inventory.wallet"], 17)
        self.assertNotIn("flag", values)
        self.assertEqual(self.store.money, 150)

    def test_wallet_selection_excludes_random_number_parameters(self):
        entries = [{"path": ["random_1_2_money", "x1"], "value": 3},
                   {"path": ["money"], "value": 18},
                   {"path": ["money_boost_counter"], "value": 64}]
        self.assertEqual(app.wallet_entries(entries), [{"path": ["money"], "value": 18}])

    def test_enable_spend_refill_disable(self):
        result = self.command("enable", path=["money"], amount=999999999)
        self.assertTrue(result["enabled"])
        self.assertEqual(self.store.money, 999999999)
        self.store.money -= 1234
        self.engine.config.python_callbacks[0]()
        self.assertEqual(self.store.money, 999999999)
        self.command("disable")
        self.store.money -= 77
        self.engine.config.interact_callbacks[0]()
        self.assertEqual(self.store.money, 999999922)
        self.assertEqual(self.store.energy, 8)

    def test_nested_attributes_and_dictionary(self):
        self.command("enable", path=["player", "cash"], amount=500)
        self.assertEqual(self.store.player.cash, 500.0)
        self.assertIsInstance(self.store.player.cash, float)
        self.command("enable", path=["inventory", "wallet"], amount=750)
        self.assertEqual(self.store.inventory["wallet"], 750)

    def test_reject_invalid_targets_and_amounts(self):
        for path, amount in [(["__dict__"], 100), (["missing"], 100), (["flag"], 100),
                             (["money"], -1), (["money"], True), (["money"], 1.5),
                             (["money"], 1000000000), (["config", "money"], 50)]:
            result = self.command("enable", path=path, amount=amount)
            self.assertFalse(result["enabled"])
            self.assertTrue(result["error"])
        self.assertEqual(self.store.money, 150)

    def test_main_menu_and_missing_loaded_variable(self):
        self.store.main_menu = True
        result = self.command("enable", path=["money"], amount=1000)
        self.assertFalse(result["enabled"])
        self.store.main_menu = False
        self.command("enable", path=["money"], amount=1000)
        del self.store.money
        self.assertTrue(self.poll()["error"])
        self.store.money = 25
        self.assertEqual(self.poll()["current"], 1000)

    def test_stale_command_never_enables(self):
        app.write_command(self.game, "enable", path=["money"], amount=999)
        file = self.game / "plaza_wallet" / "request.json"
        request = json.loads(file.read_text())
        request["time"] = time.time() - 120
        file.write_text(json.dumps(request))
        self.assertFalse(self.poll()["enabled"])
        self.assertEqual(self.store.money, 150)

    def test_quick_restart_does_not_replay_enable(self):
        app.write_command(self.game, "enable", path=["money"], amount=999)
        source = (app.BASE / app.BRIDGE).read_text(encoding="utf-8")
        body = textwrap.dedent(source.split("init 999 python hide:\n", 1)[1])
        hidden_locals = {}
        with patch.dict(sys.modules, {"renpy": self.engine}):
            exec(compile(body, app.BRIDGE, "exec"), {}, hidden_locals)
        self.namespace = hidden_locals["_plaza_wallet_context"]
        self.assertFalse(self.poll()["enabled"])
        self.assertEqual(self.store.money, 150)

    def test_install_and_remove_preserve_originals(self):
        original = self.game / "script.rpy"
        original.write_text("label start: pass")
        self.assertEqual(app.game_directory(self.root), self.game)
        self.assertEqual(app.game_directory(self.game), self.game)
        app.install_bridge(self.game)
        app.install_bridge(self.game)
        self.assertTrue((self.game / app.BRIDGE).exists())
        destination = app.uninstall_bridge(self.game)
        self.assertTrue((destination / app.BRIDGE).exists())
        self.assertFalse((self.game / app.BRIDGE).exists())
        self.assertEqual(original.read_text(), "label start: pass")

    def test_refuse_foreign_mod_collision(self):
        foreign = self.game / app.BRIDGE
        foreign.write_text("# unrelated file")
        with self.assertRaises(ValueError):
            app.install_bridge(self.game)
        self.assertEqual(foreign.read_text(), "# unrelated file")


if __name__ == "__main__":
    unittest.main(verbosity=2)
