# Wuthering Waves Launcher

A desktop launcher for **Wuthering Waves** built with Python and Kivy. It provides a polished UI for launching the game, managing localisation packs, customising the background artwork, and persisting user settings such as window size and position.

## Features

- **Game directory selector** – points to the game installation folder and launches Wuthering Waves.exe from that directory.
- **Multilingual UI** – supports pl_PL and en_US with JSON translation packs stored in assets/lang/. (You can contribue to new lang packs)
- **Custom backgrounds** – pick any image; the launcher copies it into assets/ui_assets/background.* and renders it behind the UI.
- **Persistent settings** – the launcher stores window size, window position, selected language, game folder, and background in config.json.
- **Animated sidebar** – expandable menu for navigating current (and future) screens.

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

The project ships as source, but you can create a standalone .exe using PyInstaller:

`bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name WutheringWavesLauncher \
  --add-data="assets;assets" --add-data="launcher.kv;." launcher.py
`

This command produces a dist/WutheringWavesLauncher.exe. The --add-data flags ensure the assets and KV layout are bundled next to the executable. Distribute the entire dist directory so the launcher can access its resources.

## License

Released under the MIT License.
