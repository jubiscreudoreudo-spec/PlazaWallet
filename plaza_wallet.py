# Python · plaza_wallet.py · Plaza Wallet · Windows · Python 3.10+ / Tkinter
"""A local Ren'Py wallet controller. No third-party Python dependencies."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import uuid
from i18n import LANGUAGES, CATALOGS, translate, number

BASE = Path(__file__).resolve().parent
BRIDGE = "zz_plaza_wallet.rpy"
MARKER = "PLAZA_WALLET_BRIDGE_V1"
BG = "#0c0e16"
CARD = "#171a28"
INPUT = "#10131f"
FG = "#f3f1ff"
MUTED = "#969bb5"
PURPLE = "#a78bfa"
GREEN = "#66e3b4"


def application_directory():
    """Preferences belong beside the EXE, not in PyInstaller's extraction folder."""
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else BASE


def load_settings(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return data
    except (OSError, ValueError):
        return {}


def save_settings(path, data):
    path = Path(path)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def wallet_entries(entries):
    """Only the verified wallet, never RNG parameters with 'money' in their name."""
    return [entry for entry in entries if entry.get("path") == ["money"]]


def game_directory(selected: str | Path) -> Path:
    path = Path(selected).expanduser().resolve()
    if path.is_file():
        path = path.parent
    game = path if path.name.lower() == "game" else path / "game"
    if not game.is_dir() or not (game.parent / "renpy").is_dir():
        raise ValueError("Selecione a pasta do jogo Ren'Py, com as subpastas game e renpy.")
    return game


def backup_dir(game: Path) -> Path:
    result = game.parent / "plaza_wallet_backups" / (time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6])
    result.mkdir(parents=True, exist_ok=False)
    return result


def install_bridge(game: Path) -> None:
    source = BASE / BRIDGE
    target = game / BRIDGE
    if not source.is_file():
        raise FileNotFoundError("O arquivo zz_plaza_wallet.rpy precisa ficar junto do aplicativo.")
    if target.exists():
        if MARKER not in target.read_text(encoding="utf-8"):
            raise ValueError("Ja existe um mod com esse nome, de outra origem. Nada foi alterado.")
        if target.read_bytes() == source.read_bytes():
            return
        backup = backup_dir(game)
        shutil.copy2(target, backup / target.name)
        compiled = target.with_suffix(".rpyc")
        if compiled.exists():
            shutil.copy2(compiled, backup / compiled.name)
            compiled.unlink()
    elif target.with_suffix(".rpyc").exists():
        raise ValueError("Existe um .rpyc sem o fonte correspondente. Remova esse conflito manualmente.")
    temporary = target.with_suffix(".rpy.tmp")
    shutil.copyfile(source, temporary)
    os.replace(temporary, target)
    (game / "plaza_wallet").mkdir(exist_ok=True)


def uninstall_bridge(game: Path) -> Path:
    target = game / BRIDGE
    if not target.exists() or MARKER not in target.read_text(encoding="utf-8"):
        raise ValueError("O mod Plaza Wallet nao foi encontrado nesta pasta.")
    backup = backup_dir(game)
    for item in (target, target.with_suffix(".rpyc")):
        if item.is_file():
            shutil.move(str(item), str(backup / item.name))
    ipc = game / "plaza_wallet"
    # Only move our known files; leave any unrelated user files in place.
    for name in ("request.json", "response.json", "request.tmp"):
        if (ipc / name).is_file():
            shutil.move(str(ipc / name), str(backup / name))
    return backup


def write_command(game: Path, action: str, **params) -> str:
    folder = game / "plaza_wallet"
    folder.mkdir(exist_ok=True)
    identity = uuid.uuid4().hex
    payload = {"id": identity, "time": time.time(), "action": action, **params}
    temporary = folder / "request.tmp"
    temporary.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")
    os.replace(temporary, folder / "request.json")
    return identity


class Wallet(tk.Tk):
    def __init__(self, language=None, settings_path=None):
        super().__init__()
        self.settings_path = Path(settings_path) if settings_path else application_directory() / "settings.local.json"
        settings = load_settings(self.settings_path)
        preferred = language or settings.get("language", "pt-BR")
        self.language = preferred if isinstance(preferred, str) and preferred in LANGUAGES else "en"
        self._started = False
        self.title("Plaza Wallet")
        self.geometry("1000x760")
        self.minsize(1000, 760)
        self.configure(bg=BG)
        self.game: Path | None = None
        self.entries: list[dict] = []
        self.response: dict = {}
        self.pending: tuple[str, float] | None = None
        self.online = False
        self.last_entries = None
        self.path_text = tk.StringVar(value=self.tr("Selecione a pasta de instalação do jogo"))
        self.filter_text = tk.StringVar()
        self.amount = tk.StringVar(value="3000")
        self.status = tk.StringVar(value=self.tr("Aguardando o jogo"))
        self.details = tk.StringVar(value=self.tr("Instale o conector e abra uma partida para começar."))
        self.selected_text = tk.StringVar(value=self.tr("Nenhuma variável selecionada"))
        self.balance_text = tk.StringVar(value="—")
        self.mode_text = tk.StringVar(value=self.tr("DESATIVADO"))
        self._style()
        self.filter_text.trace_add("write", lambda *_: self.render_entries() if self._started else None)
        try:
            self.game = game_directory(settings["game_path"])
            self.path_text.set(str(self.game.parent))
            self.filter_text.set("money")
            amount = int(settings.get("amount", 3000))
            self.amount.set(str(amount if 1 <= amount <= 999999999 else 3000))
            self.details.set(self.tr("Pasta lembrada. Carregue uma partida e clique em Ler jogo."))
        except (OSError, ValueError, KeyError, TypeError):
            pass
        self.protocol("WM_DELETE_WINDOW", self.close)
        if language is None:
            self.show_language_picker()
        else:
            self.start_wallet()
        self.after(500, self.poll)

    def tr(self, message, **values):
        return translate(self.language, message, **values)

    def error_text(self, error):
        message = str(error)
        if message in CATALOGS["pt-BR"]:
            return self.tr(message)
        return self.tr("Falha na operação. Detalhes do sistema: {detail}", detail=message)

    def remember(self):
        try:
            save_settings(self.settings_path, {
                "language": self.language,
                "game_path": str(self.game.parent) if self.game else "",
                "amount": int(self.amount.get()) if self.amount.get().isdigit() else 3000,
            })
            return True
        except (OSError, ValueError) as exc:
            self.details.set(self.tr("Não foi possível salvar suas preferências. {detail}", detail=str(exc)))
            return False

    def show_language_picker(self):
        self._started = False
        for child in self.winfo_children():
            child.destroy()
        self.geometry("1000x760")
        card = tk.Frame(self, bg=CARD, padx=50, pady=36)
        card.place(relx=0.5, rely=0.5, anchor="center", width=640, height=560)
        self.label(card, "P / W", size=30, color=PURPLE, bold=True).pack(anchor="w")
        self.label(card, "PLAZA WALLET", size=10, bold=True).pack(anchor="w", pady=(4, 20))
        self.picker_title = self.label(card, self.tr("Escolha seu idioma"), size=24, bold=True)
        self.picker_title.pack(anchor="w")
        self.picker_subtitle = self.label(card, self.tr("Como você quer usar o Plaza Wallet?"), color=MUTED)
        self.picker_subtitle.pack(anchor="w", pady=(6, 18))
        self.language_choice = tk.StringVar(value=self.language)
        for code, name in LANGUAGES.items():
            tk.Radiobutton(card, text=name, value=code, variable=self.language_choice,
                           command=self.preview_language, bg=CARD, fg=FG,
                           activebackground=CARD, activeforeground=PURPLE,
                           selectcolor=INPUT, font=("Segoe UI", 12),
                           anchor="w", cursor="hand2").pack(fill="x", pady=5)
        self.continue_button = self.button(card, self.tr("Continuar"), self.start_wallet, primary=True)
        self.continue_button.pack(fill="x", pady=(22, 12))
        self.picker_hint = self.label(card, self.tr("Você pode trocar o idioma a qualquer momento."), size=9, color=MUTED)
        self.picker_hint.pack(anchor="w")

    def preview_language(self):
        self.language = self.language_choice.get()
        self.picker_title.configure(text=self.tr("Escolha seu idioma"))
        self.picker_subtitle.configure(text=self.tr("Como você quer usar o Plaza Wallet?"))
        self.continue_button.configure(text=self.tr("Continuar"))
        self.picker_hint.configure(text=self.tr("Você pode trocar o idioma a qualquer momento."))

    def start_wallet(self):
        for child in self.winfo_children():
            child.destroy()
        self.path_text.set(str(self.game.parent) if self.game else self.tr("Selecione a pasta de instalação do jogo"))
        self.status.set(self.tr("Aguardando o jogo"))
        self.mode_text.set(self.tr("DESATIVADO"))
        self.selected_text.set(self.tr("Nenhuma variável selecionada"))
        self.details.set(self.tr("Pasta lembrada. Carregue uma partida e clique em Ler jogo.") if self.game else self.tr("Instale o conector e abra uma partida para começar."))
        self._layout()
        self._started = True
        self.render_entries()
        if self.tree.exists("0"):
            self.tree.selection_set("0")
            self.select()
        self.remember()

    def _style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview", background=INPUT, foreground=FG,
                        fieldbackground=INPUT, borderwidth=0, rowheight=32,
                        bordercolor=INPUT, lightcolor=INPUT, darkcolor=INPUT,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=CARD, foreground=MUTED,
                        borderwidth=0, font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", "#49386f")],
                  foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading", background=[("active", CARD)])
        style.configure("Vertical.TScrollbar", background="#34394e", troughcolor=INPUT,
                        borderwidth=0, arrowcolor=MUTED, bordercolor=INPUT,
                        lightcolor=INPUT, darkcolor=INPUT)

    def label(self, parent, text=None, variable=None, size=10, color=FG, bold=False, **kwargs):
        return tk.Label(parent, text=text, textvariable=variable,
                        font=("Segoe UI", size, "bold" if bold else "normal"),
                        bg=parent.cget("bg"), fg=color, anchor="w", **kwargs)

    def button(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command,
                         font=("Segoe UI", 10, "bold"), cursor="hand2",
                         relief="flat", bd=0, padx=17, pady=10,
                         bg=PURPLE if primary else "#292d42",
                         fg="#161023" if primary else FG,
                         activebackground="#bba6ff" if primary else "#373d57",
                         activeforeground="#161023" if primary else FG)

    def entry(self, parent, variable):
        return tk.Entry(parent, textvariable=variable, bg=INPUT, fg=FG,
                        insertbackground=PURPLE, relief="flat", bd=10,
                        font=("Segoe UI", 11), highlightthickness=1,
                        highlightbackground="#30354b", highlightcolor=PURPLE)

    def _layout(self):
        sidebar = tk.Frame(self, bg="#111320", width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self.label(sidebar, "P / W", size=26, color=PURPLE, bold=True).pack(anchor="w", padx=24, pady=(28, 0))
        self.label(sidebar, "PLAZA WALLET", size=10, bold=True).pack(anchor="w", padx=24, pady=(4, 38))
        nav = tk.Frame(sidebar, bg="#2d2446")
        nav.pack(fill="x", padx=14)
        self.label(nav, self.tr("◈   Carteira"), color="#cdbdff", bold=True).pack(padx=14, pady=13)
        self.label(sidebar, self.tr("CONTROLE LOCAL"), size=9, color=MUTED).pack(anchor="w", padx=24, pady=(32, 10))
        self.label(sidebar, self.tr("01  Conectar\n\n02  Encontrar saldo\n\n03  Ativar reposição"), color=MUTED, justify="left").pack(anchor="w", padx=24)
        self.button(sidebar, self.tr("Idioma"), self.show_language_picker).pack(fill="x", padx=14, pady=(30, 0))
        self.label(sidebar, "PYTHON + REN’PY\nv1.2  /  Windows", size=9, color=MUTED, justify="left").pack(side="bottom", anchor="w", padx=24, pady=25)

        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=28, pady=24)
        self.label(main, "MILF’S PLAZA", size=9, color=PURPLE, bold=True).pack(anchor="w")
        self.label(main, self.tr("Sua carteira. Sem limites."), size=24, bold=True).pack(anchor="w", pady=(4, 5))
        self.label(main, self.tr("Escolha o saldo e mantenha o dinheiro sempre disponível."), color=MUTED).pack(anchor="w", pady=(0, 18))

        connect = tk.Frame(main, bg=CARD, padx=16, pady=12)
        connect.pack(fill="x")
        row = tk.Frame(connect, bg=CARD)
        row.pack(fill="x")
        self.label(row, self.tr("01 / CONEXÃO"), size=9, color=MUTED, bold=True).pack(side="left")
        self.connection_label = self.label(row, variable=self.status, size=9, color=PURPLE)
        self.connection_label.pack(side="right")
        self.label(connect, variable=self.path_text, color=FG, wraplength=620).pack(anchor="w", pady=9)
        row = tk.Frame(connect, bg=CARD)
        row.pack(fill="x")
        self.button(row, self.tr("Escolher pasta"), self.choose).pack(side="left")
        self.button(row, self.tr("Instalar conector"), self.install).pack(side="left", padx=8)
        self.button(row, self.tr("Remover"), self.uninstall).pack(side="right")

        area = tk.Frame(main, bg=BG)
        area.pack(fill="both", expand=True, pady=(18, 14))
        left = tk.Frame(area, bg=CARD, padx=16, pady=14)
        left.pack(side="left", fill="both", expand=True)
        row = tk.Frame(left, bg=CARD)
        row.pack(fill="x")
        self.label(row, self.tr("02 / ENCONTRAR SALDO"), size=9, color=MUTED, bold=True).pack(side="left")
        self.scan_button = self.button(row, self.tr("Ler jogo"), self.scan)
        self.scan_button.pack(side="right")
        self.entry(left, self.filter_text).pack(fill="x", pady=(12, 4))
        self.label(left, self.tr("Filtre por nome ou pelo valor atual do dinheiro."), size=9, color=MUTED).pack(anchor="w", pady=(0, 9))
        table = tk.Frame(left, bg=INPUT)
        table.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(table, columns=("name", "value"), show="headings", selectmode="browse", height=6)
        self.tree.heading("name", text=self.tr("VARIÁVEL"))
        self.tree.heading("value", text=self.tr("VALOR"))
        self.tree.column("name", width=190, minwidth=90)
        self.tree.column("value", width=100, minwidth=60, anchor="e")
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.select)
        self.tree.tag_configure("money", foreground=GREEN)

        right = tk.Frame(area, bg=CARD, padx=18, pady=16, width=260)
        right.pack(side="left", fill="y", padx=(14, 0))
        right.pack_propagate(False)
        self.label(right, self.tr("03 / DINHEIRO INFINITO"), size=9, color=MUTED, bold=True).pack(anchor="w")
        self.mode_label = self.label(right, variable=self.mode_text, size=9, color=MUTED, bold=True)
        self.mode_label.pack(anchor="w", pady=(18, 3))
        self.label(right, variable=self.balance_text, size=22, bold=True).pack(anchor="w")
        self.label(right, variable=self.selected_text, size=9, color=PURPLE, wraplength=220).pack(anchor="w", pady=(5, 18))
        self.label(right, self.tr("Saldo mínimo"), size=10, color=MUTED).pack(anchor="w", pady=(0, 5))
        self.entry(right, self.amount).pack(fill="x")
        self.enable_button = self.button(right, self.tr("Ativar reposição ∞"), self.enable, primary=True)
        self.enable_button.pack(fill="x", pady=(14, 8))
        self.disable_button = self.button(right, self.tr("Desativar"), self.disable)
        self.disable_button.pack(fill="x")

        self.label(main, variable=self.details, size=9, color=MUTED, wraplength=720, justify="left").pack(anchor="w")
        self.label(main, self.tr("Primeiro uso: instale com o jogo fechado; depois abra e carregue uma partida."), size=9, color=MUTED, wraplength=720).pack(anchor="w", pady=(7, 0))
        self.update_buttons()

    def choose(self):
        path = filedialog.askdirectory(title=self.tr("Pasta do MILF's Plaza"))
        if not path:
            return
        if self.online and self.response.get("enabled"):
            messagebox.showinfo(self.tr("Conector ativo"), self.tr("Desative a reposição antes de trocar de pasta."))
            return
        try:
            self.game = game_directory(path)
            self.path_text.set(str(self.game.parent))
            self.entries = []
            self.last_entries = None
            self.pending = None
            self.response = {}
            self.online = False
            self.render_entries()
            self.details.set(self.tr("Pasta selecionada. Instale o conector com o jogo fechado."))
            self.remember()
        except (OSError, ValueError) as exc:
            messagebox.showerror(self.tr("Pasta inválida"), self.error_text(exc))

    def install(self):
        if self.game is None:
            self.choose()
        if self.game is None:
            return
        if self.online:
            messagebox.showinfo(self.tr("Feche o jogo"), self.tr("Feche o jogo antes de instalar ou atualizar o conector."))
            return
        try:
            install_bridge(self.game)
            self.details.set(self.tr("Conector instalado. Abra o jogo, carregue sua partida e clique em Ler jogo."))
        except (OSError, ValueError) as exc:
            messagebox.showerror(self.tr("Falha ao instalar"), self.error_text(exc))

    def uninstall(self):
        if self.game is None:
            return
        if self.online:
            messagebox.showinfo(self.tr("Feche o jogo"), self.tr("Feche o jogo antes de remover o conector."))
            return
        try:
            destination = uninstall_bridge(self.game)
            self.details.set(self.tr("Conector removido. Cópia guardada em {path}", path=str(destination)))
        except (OSError, ValueError) as exc:
            messagebox.showerror(self.tr("Falha ao remover"), self.error_text(exc))

    def send(self, action, **params):
        if not self.online or self.game is None:
            self.details.set(self.tr("Abra o jogo com o conector instalado e carregue sua partida."))
            return
        if self.pending:
            return
        try:
            identity = write_command(self.game, action, **params)
            self.pending = (identity, time.time())
            self.details.set(self.tr("Aguardando confirmação do jogo…"))
            self.update_buttons()
        except OSError as exc:
            messagebox.showerror(self.tr("Falha de comunicação"), self.error_text(exc))

    def scan(self):
        self.send("scan")

    def enable(self):
        selected = self.tree.selection()
        if not selected:
            self.details.set(self.tr("Selecione a variável que corresponde ao dinheiro da sua partida."))
            return
        try:
            amount = int(self.amount.get().strip())
            if not 1 <= amount <= 999999999:
                raise ValueError
        except ValueError:
            messagebox.showerror(self.tr("Saldo inválido"), self.tr("Digite um inteiro entre 1 e 999999999, sem separadores."))
            return
        self.send("enable", path=["money"], amount=amount)
        self.remember()

    def disable(self):
        self.send("disable")

    def select(self, _event=None):
        if not self._started:
            return
        selection = self.tree.selection()
        if selection:
            entry = self.entries[int(selection[0])]
            self.selected_text.set(entry["name"])
            if not self.response.get("enabled"):
                self.balance_text.set(self.format_value(entry["value"]))
        else:
            self.selected_text.set(self.tr("Nenhuma variável selecionada"))
        self.update_buttons()

    def format_value(self, value):
        return number(self.language, value)

    def render_entries(self):
        selection = self.tree.selection()
        selected_path = None
        if selection and int(selection[0]) < len(self.entries):
            selected_path = self.entries[int(selection[0])]["path"]
        self.tree.delete(*self.tree.get_children())
        term = self.filter_text.get().strip().lower()
        for index, entry in enumerate(self.entries):
            value = self.format_value(entry["value"])
            if term and term not in entry["name"].lower() and term not in str(entry["value"]).lower() and term not in value:
                continue
            money = any(word in entry["name"].lower() for word in ("money", "cash", "wallet", "dinheiro", "balance", "dollar"))
            self.tree.insert("", "end", iid=str(index), values=(entry["name"], value), tags=("money",) if money else ())
            if selected_path == entry["path"]:
                self.tree.selection_set(str(index))
        self.select()

    def update_buttons(self):
        if not self._started:
            return
        ready = self.online and self.pending is None
        self.scan_button.configure(state="normal" if ready else "disabled")
        self.enable_button.configure(state="normal" if ready and self.tree.selection() else "disabled")
        self.disable_button.configure(state="normal" if ready and self.response.get("enabled") else "disabled")

    def poll(self):
        if not self._started:
            self.after(500, self.poll)
            return
        try:
            self.online = False
            if self.game:
                file = self.game / "plaza_wallet" / "response.json"
                try:
                    data = json.loads(file.read_text(encoding="utf-8"))
                    if data.get("protocol") == 1 and abs(time.time() - data["time"]) < 4:
                        self.response = data
                        self.online = True
                except (OSError, ValueError, KeyError, TypeError):
                    # Brief partial writes are expected; keep the last valid heartbeat.
                    self.online = bool(self.response and abs(time.time() - self.response.get("time", 0)) < 4)
            if self.online:
                data = self.response
                self.status.set(self.tr("●  Jogo conectado"))
                self.connection_label.configure(fg=GREEN)
                entries = wallet_entries(data.get("entries", []))
                if entries != self.last_entries:
                    self.tree.selection_remove(*self.tree.selection())
                    self.entries = entries
                    self.last_entries = entries
                    self.render_entries()
                    for index, entry in enumerate(self.entries):
                        if entry["path"] == ["money"] and self.tree.exists(str(index)):
                            self.tree.selection_set(str(index))
                            self.tree.see(str(index))
                            self.select()
                            break
                active = data.get("enabled", False)
                self.mode_text.set(self.tr("REPOSIÇÃO ATIVA") if active else self.tr("DESATIVADO"))
                self.mode_label.configure(fg=GREEN if active else MUTED)
                if active:
                    self.balance_text.set(self.format_value(data.get("current")))
                    self.selected_text.set(".".join(data.get("path") or []))
                if self.pending and data.get("id") == self.pending[0]:
                    self.pending = None
                    self.details.set(self.error_text(data["error"]) if data.get("error") else (self.tr("Reposição confirmada pelo jogo.") if active else self.tr("Conectado. {count} variáveis lidas. Selecione o dinheiro pelo nome e valor.", count=len(self.entries))))
                elif data.get("error"):
                    self.details.set(self.error_text(data["error"]))
            else:
                self.status.set(self.tr("○  Aguardando o jogo"))
                self.connection_label.configure(fg=MUTED)
                self.mode_text.set(self.tr("SEM CONEXÃO"))
                self.mode_label.configure(fg=MUTED)
            if self.pending and time.time() - self.pending[1] > 8:
                self.pending = None
                self.details.set(self.tr("O jogo não confirmou o comando. Volte à partida e tente novamente."))
            self.update_buttons()
        finally:
            self.after(500, self.poll)

    def close(self):
        if self.online and self.response.get("enabled"):
            if not messagebox.askokcancel(self.tr("Reposição ativa"), self.tr("A reposição continuará até fechar o jogo. Fechar apenas o painel?")):
                return
        self.destroy()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Plaza Wallet")
    parser.add_argument("--self-test", type=Path, metavar="REPORT_JSON", help="Check the packaged app without accessing a real game.")
    args = parser.parse_args()
    if args.self_test:
        from executable_check import run
        raise SystemExit(run(args.self_test, Wallet, install_bridge, BASE / BRIDGE))
    Wallet().mainloop()
