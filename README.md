# Plaza Wallet

A local Python money panel for **MILF's Plaza**, with a dark interface, automatic refill and language selection at startup.

[Português](LEIA-ME.md) · [Español](LEEME.md)

## Languages

Choose **Português (Brasil)**, **English** or **Español** whenever the app opens. Your last choice is preselected. Use **Language** in the sidebar to change it without restarting the game. Buttons, instructions, status, application errors and number formatting follow the chosen language. Native file dialogs and operating-system error details follow Windows settings. This translates the panel, not the game.

## Getting started

The **Windows EXE release needs no Python installation**. Extract the Windows ZIP and open **PlazaWallet.exe**. The connector and translations are embedded. Keep the EXE in a writable folder so it can remember preferences.

Running from source requires Windows and **Python 3.10+ with Tkinter**; no pip packages are needed to run the source. Both editions need a Ren'Py game installation that accepts additional `.rpy` files.

1. Extract the download. Open **PlazaWallet.exe**, or **Start.bat** / **Iniciar.bat** when using the source edition.
2. Select your language and press **Continue**.
3. Click **Choose folder** and select the game directory containing `game` and `renpy`.
4. With the game closed, click **Install connector**.
5. Launch the game, load your save, then click **Read game** in the panel.
6. The wallet variable `money` is selected automatically. Set the minimum balance and click **Enable refill ∞**. Wait for confirmation from the game.

Default balance: **3,000**. Game version **18b22** contains a rule that reduces larger balances to 3,000. Refill restores the minimum after Python blocks and during interactions, with periodic checks too. Activation and the live balance were verified in 18b22 with Ren'Py 8.3.7. Spending/refill behavior is covered by simulated-engine tests. Other versions have not been verified.

## Preferences and removal

The app saves your language, game folder and balance in **settings.local.json** next to the application. Git ignores this file. `settings.example.json` documents the format; editing it is optional. The app folder must be writable to remember preferences. If it is read-only, the panel can still run but reports the saving error.

**Disable** stops refill and leaves the current balance unchanged. Closing only the panel leaves refill active until the game closes. Restarting the game starts with refill disabled.

The panel does not edit save files directly. Saves created by the game after activation may contain the changed balance; load an earlier save to return to the previous value. To uninstall, close the game and click **Remove**. Connector files move to `plaza_wallet_backups` outside `game`. Original game scripts are not replaced.

## Troubleshooting

- No connection: check the folder, install the connector and fully restart the game.
- No wallet: load a save and click **Read game**. Only `money` is displayed.
- Write error: the connector needs permission to write to `game/plaza_wallet`.
- Startup error after installing: close the game and click **Remove**, or move `zz_plaza_wallet.rpy` and `zz_plaza_wallet.rpyc` outside `game`.
- Connector updates require a game restart. Translation-only updates require only a panel restart.

## Development and publishing

Run `python plaza_wallet.py` to open the app. Run `python -m unittest discover -v` from the project folder for tests. GUI tests require a desktop session with Tkinter.

Translations are in **i18n.py**. `ROWS` stores Portuguese source strings and their English/Spanish translations. Preserve placeholders such as `{path}`, `{count}` and `{detail}`. Tests check translations, formatting, preferences, language switching, status messages and bridge behavior.

Publish the files from the clean release ZIP. Exclude `settings.local.json`, game files, saves, logs, generated `.rpyc` files and backups. The included `.gitignore` covers local artifacts. No game assets are bundled.

Run `python build_release.py` to generate `dist/PlazaWallet.zip` from an explicit file list. Local preferences and generated files are excluded automatically.

### Build the EXE

On Windows with Python installed, run `python -m pip install -r requirements-build.txt`, then `python build_exe.py`. The result is `dist/PlazaWallet.exe`. Only the connector resource is bundled as data; personal preferences and game files are excluded. Build folders are ignored by Git.

The packaged app supports `PlazaWallet.exe --self-test report.json` to check the language screens, settings and connector installation in an isolated temporary folder. It does not access a real game. Packaging uses [PyInstaller](https://www.pyinstaller.org/en/stable/usage.html).

References: [Ren'Py callbacks](https://www.renpy.org/doc/html/config.html#callbacks) and [save behavior](https://www.renpy.org/doc/html/save_load_rollback.html).
