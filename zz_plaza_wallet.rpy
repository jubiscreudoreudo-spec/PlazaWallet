# Python / Ren'Py · zz_plaza_wallet.rpy · Plaza Wallet · Windows · Ren'Py 7/8
# PLAZA_WALLET_BRIDGE_V1 - installed by Plaza Wallet.

init 999 python hide:
    def install_bridge_callbacks():
        import os
        import io
        import json
        import time
        import math
        import types
        import renpy
        try:
            import builtins as python_builtins
        except ImportError:
            import __builtin__ as python_builtins

        # Ren'Py replaces store.list/store.dict with rollback-aware subclasses.
        # JSON returns ordinary Python containers, so validate against the originals.
        list = python_builtins.list
        dict = python_builtins.dict
        int = python_builtins.int
        float = python_builtins.float
        bool = python_builtins.bool
        str = python_builtins.str
        type = python_builtins.type

        try:
            number_types = (int, long, float)
            text_types = (str, unicode)
        except NameError:
            number_types = (int, float)
            text_types = (str,)

        folder = os.path.join(renpy.config.gamedir, "plaza_wallet")
        request_file = os.path.join(folder, "request.json")
        response_file = os.path.join(folder, "response.json")
        state = {"enabled": False, "path": None, "amount": 999999999,
                 "last_id": None, "last_poll": 0, "entries": [], "error": "",
                 "current": None, "busy": False}
        # Ignore even a very recent command left by a previous game process.
        try:
            if os.path.getsize(request_file) <= 8192:
                with io.open(request_file, "r", encoding="utf-8") as handle:
                    state["last_id"] = json.load(handle).get("id")
        except (OSError, IOError, ValueError, AttributeError):
            pass

        def numeric(value):
            return (isinstance(value, number_types) and not isinstance(value, bool)
                    and not math.isnan(float(value)) and not math.isinf(float(value)))

        def validate_path(path):
            if not isinstance(path, list) or not 1 <= len(path) <= 3:
                raise ValueError("Caminho de variavel invalido.")
            for part in path:
                if (not isinstance(part, text_types) or not part
                        or part.startswith("_") or len(part) > 128):
                    raise ValueError("Nome de variavel invalido.")
            if path[0] in ("config", "renpy", "persistent", "preferences", "gui"):
                raise ValueError("Variavel interna do motor nao pode ser alterada.")

        def get_member(obj, key):
            if isinstance(obj, dict):
                return obj[key]
            # Read stored attributes only; do not execute property getters.
            return vars(obj)[key]

        def resolve(path):
            validate_path(path)
            obj = renpy.store
            for key in path[:-1]:
                obj = get_member(obj, key)
            value = get_member(obj, path[-1])
            if not numeric(value):
                raise ValueError("A variavel selecionada nao e um numero.")
            return obj, path[-1], value

        def enforce():
            if not state["enabled"] or state["busy"]:
                return
            state["busy"] = True
            try:
                # Do not create a variable on title screens or before loading a save.
                if getattr(renpy.store, "main_menu", False):
                    state["current"] = None
                    return
                obj, key, value = resolve(state["path"])
                if value < state["amount"]:
                    amount = float(state["amount"]) if isinstance(value, float) else state["amount"]
                    if isinstance(obj, dict):
                        obj[key] = amount
                    else:
                        setattr(obj, key, amount)
                    value = amount
                state["current"] = value
                state["error"] = ""
            except (KeyError, AttributeError):
                state["current"] = None
                state["error"] = "Variavel ausente neste momento. Carregue o save correto."
            except Exception as exc:
                state["enabled"] = False
                state["error"] = str(exc)
            finally:
                state["busy"] = False

        def scan():
            found = []
            visited = set()
            excluded = {"config", "renpy", "persistent", "preferences", "gui"}

            def walk(obj, prefix, depth):
                if id(obj) in visited or len(found) >= 3000:
                    return
                visited.add(id(obj))
                if isinstance(obj, dict):
                    items = list(obj.items())
                else:
                    try:
                        items = list(vars(obj).items())
                    except TypeError:
                        return
                for key, value in items:
                    if len(found) >= 3000:
                        break
                    if (not isinstance(key, text_types) or not key or key.startswith("_")
                            or len(key) > 128 or (not prefix and key in excluded)):
                        continue
                    path = prefix + [key]
                    try:
                        is_number = numeric(value)
                    except (OverflowError, ValueError):
                        is_number = False
                    if is_number:
                        found.append({"path": path, "name": ".".join(path), "value": value})
                    elif depth < 2 and not isinstance(value, (types.ModuleType, type)) and not callable(value):
                        walk(value, path, depth + 1)
            walk(renpy.store, [], 0)
            found.sort(key=lambda item: item["name"].lower())
            state["entries"] = found

        def process_command(command):
            action = command.get("action")
            if action == "scan":
                scan()
            elif action == "enable":
                path = command.get("path")
                amount = command.get("amount")
                if isinstance(amount, bool) or not isinstance(amount, number_types) or int(amount) != amount or not 1 <= amount <= 999999999:
                    raise ValueError("Saldo deve estar entre 1 e 999999999.")
                if getattr(renpy.store, "main_menu", False):
                    raise ValueError("Carregue uma partida antes de ativar.")
                resolve(path)
                state.update(path=path, amount=int(amount), enabled=True, error="")
                enforce()
            elif action == "disable":
                state.update(enabled=False, error="")
            else:
                raise ValueError("Comando desconhecido.")

        def poll():
            now = time.time()
            if now - state["last_poll"] < 0.4:
                return
            state["last_poll"] = now
            try:
                if os.path.isfile(request_file) and os.path.getsize(request_file) <= 8192:
                    with io.open(request_file, "r", encoding="utf-8") as handle:
                        command = json.load(handle)
                    if command.get("id") != state["last_id"]:
                        state["last_id"] = command.get("id")
                        state["error"] = ""
                        # Commands expire, so restarting a game never enables an old request.
                        if abs(now - float(command.get("time", 0))) < 15:
                            try:
                                process_command(command)
                            except Exception as exc:
                                state["error"] = str(exc)
                enforce()
                if not os.path.isdir(folder):
                    os.makedirs(folder)
                response = {"protocol": 1, "time": now, "id": state["last_id"],
                            "enabled": state["enabled"], "path": state["path"],
                            "amount": state["amount"], "current": state["current"],
                            "entries": state["entries"], "error": state["error"],
                            "game": str(renpy.config.name), "version": str(renpy.config.version)}
                # The reader retries on partial JSON, and never treats it as success.
                with io.open(response_file, "w", encoding="utf-8") as handle:
                    handle.write(json.dumps(response, ensure_ascii=True))
            except Exception as exc:
                renpy.log("Plaza Wallet: " + str(exc))

        renpy.config.interact_callbacks.append(enforce)
        renpy.config.python_callbacks.append(enforce)
        renpy.config.periodic_callbacks.append(poll)

        return {"state": state, "poll": poll}

    _plaza_wallet_context = install_bridge_callbacks()
