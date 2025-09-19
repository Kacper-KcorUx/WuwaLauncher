# Wuthering Waves Launcher

A desktop launcher for **Wuthering Waves** built with Python and Kivy. It provides a polished UI for launching the game, managing localisation packs, customising the background artwork, and persisting user settings such as window size and position.

## Features

- **Game directory selector** - points to the game installation folder and launches `WutheringWaves.exe` from there.
- **Multilingual UI** - ships with `pl_PL` and `en_US` JSON translation packs stored inside `assets/lang/`.
- **Custom backgrounds** - pick any image; the launcher copies it into `user_data/assets/ui_assets/background.*` and renders it behind the UI.
- **Persistent settings** - configuration is stored in an editable `config.json` that lives next to the packaged executable.
- **Animated sidebar** - expandable menu for navigating current (and future) screens.

## Project structure

```text
assets/
  lang/            # Translation packs (JSON)
  ui_assets/       # Default background image (background.*)
launcher.py        # Application entry point (logic + KV fallback)
launcher.kv        # Main Kivy layout
config.json        # Default configuration used on first launch
requirements.txt   # Python dependencies
```

## Getting started

```bash
# 1. Clone the repository
git clone https://github.com/Kacper-KcorUx/WuwaLauncher.git
cd WuwaLauncher

# 2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Run the launcher
python launcher.py
```

The first launch creates default folders inside `assets/` (for shipped resources) and `user_data/` (for per-user overrides) and initialises `config.json`. Use the **Settings** screen to point the launcher at your game directory, choose a language, and select a background image.

## Runtime layout when packaged

When the launcher is frozen with PyInstaller in `onedir` mode the output folder looks like this:

```text
dist/WutheringWavesLauncher/
  WutheringWavesLauncher.exe    # Frozen Python entry point
  assets/                       # Editable localisation packs and default UI assets
  config.json                   # Editable configuration shared by the launcher
  user_data/                    # Created on first run for user-provided assets
  ...                           # PyInstaller bootstrap libraries
```

Feel free to edit `assets/`, `config.json`, or files inside `user_data/` between runs.

## Building a Windows executable

Run PyInstaller in `onedir` mode so only the Python bytecode lands inside the executable and all resources stay editable alongside it:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name WutheringWavesLauncher \
  --add-data "assets;assets" \
  --add-data "config.json;." \
  --add-data "launcher.kv;." launcher.py
```

The build produces `dist/WutheringWavesLauncher/`. Zip and distribute that folder so the launcher can access its resources.

## Continuous delivery

The repository includes a GitHub Actions workflow that builds the Windows package on pushes, manual triggers, and tagged releases. Release builds automatically upload the zipped `dist/WutheringWavesLauncher` directory as a downloadable asset.

## License

Released under the MIT License. Adapt as needed for your project.
