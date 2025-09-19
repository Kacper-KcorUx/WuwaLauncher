# Wuthering Waves Launcher

A desktop launcher for **Wuthering Waves** built with Python and Kivy. It provides a polished UI for launching the game, managing localisation packs, customising the background artwork, and persisting user settings such as window size and position.

## Features

- **Game directory selector** - points to the game installation folder and launches Wuthering Waves.exe from that directory.
- **Multilingual UI** - supports pl_PL and en_US with JSON translation packs stored in `assets/lang/`, and you can drop custom packs into `user_data/assets/lang/` without touching the bundled files.
- **Custom backgrounds** - pick any image; the launcher copies it into assets/ui_assets/background.* and renders it behind the UI.
- **Persistent settings** - the launcher stores preferences in `config.json` and the `user_data/` folder created next to the `.exe`, so moving the folder keeps your settings.

## Project structure

`	ext
├─ assets/
│  ├─ lang/            # Translation packs (JSON)
│  └─ ui_assets/       # Background image (background.*)
├─ launcher.py         # Application entry point (logic + KV fallback)
├─ launcher.kv         # Main Kivy layout
├─ config.json         # Saved user preferences
└─ requirements.txt    # Python dependencies
`

## Getting started

# 1. Clone the repository

git clone https://github.com/Kacper-KcorUx/WuwaLauncher.git

cd WuwaLauncher

# 2. Install dependencies

pip install --upgrade pip

pip install -r requirements.txt

# 3. Run the launcher
python launcher.py
`

The first launch creates default folders inside assets/ and initialises config.json. Use the **Settings** screen to point the launcher at your game directory, choose a language, and select a background image.

## Building a Windows executable

The project ships as source, but you can create a standalone onedir build using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name WutheringWavesLauncher ^
  --add-data "assets;assets" ^
  --add-data "config.json;." ^
  --add-data "launcher.kv;." launcher.py
```

This command produces the folder `dist/WutheringWavesLauncher/` with the executable and bundled resources. Distribute the entire directory (for example by zipping it) so the launcher keeps access to its data.

## Installing the .exe

1. Download the `WutheringWavesLauncher-win64.zip` archive from GitHub Releases or build it yourself using the steps above.
2. Extract the `WutheringWavesLauncher` folder somewhere with write permissions (for example `D:\Games\WutheringWavesLauncher`).
3. Launch `WutheringWavesLauncher.exe` directly or create a desktop shortcut that points to it.
4. Settings and user data (`config.json`, `user_data/`) live in the same directory, so copying that folder migrates all preferences.
   Drop community language packs into `user_data/assets/lang/<language_code>/messages.json` if you need additional translations.

## License

Released under the MIT License.
