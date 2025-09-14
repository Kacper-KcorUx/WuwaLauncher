from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Delayed import of Kivy to provide a friendly message if missing
try:
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.properties import BooleanProperty, StringProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.metrics import dp
except Exception as e:  # pragma: no cover - import-time helper
    missing = "kivy" if isinstance(e, ModuleNotFoundError) else None
    print(
        "Nie znaleziono biblioteki Kivy. Zainstaluj zależności i spróbuj ponownie.\n"
        "Polecenie: pip install -r requirements.txt\n\nSzczegóły:",
        e,
        file=sys.stderr,
    )
    # Wyjście tylko, jeśli uruchamiamy ten plik bez Kivy
    if __name__ == "__main__":
        sys.exit(1)


APP_TITLE = "Wuthering Waves Launcher"
CONFIG_FILE = Path(__file__).with_name("config.json")
KV_FILE = Path(__file__).with_name("launcher.kv")


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(cfg: dict) -> None:
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def info_popup(title: str, message: str) -> None:
    Popup(
        title=title,
        content=Label(text=message, padding=(dp(12), dp(12))),
        size_hint=(0.6, 0.35),
        auto_dismiss=True,
    ).open()


class LauncherRoot(BoxLayout):
    game_path = StringProperty("")
    can_play = BooleanProperty(False)
    status_text = StringProperty("Plik gry: nie ustawiono")

    def refresh_state(self):
        p = Path(self.game_path) if self.game_path else None
        ok = bool(p and p.exists())
        self.can_play = ok
        self.status_text = f"Plik gry: {p}" if ok else "Plik gry: nie ustawiono"

    def open_file_dialog(self):
        app = App.get_running_app()
        # Najpierw spróbuj natywnego okna Windows (przez tkinter)
        try:
            if sys.platform == "win32" and hasattr(app, "open_native_dialog"):
                path = app.open_native_dialog()
                if path:
                    app.on_file_chosen(path, None)
                    return
        except Exception:
            pass

        # Fallback: popup Kivy FileChooser
        from kivy.factory import Factory
        popup = Factory.FileChooserPopup()
        if app.initial_dir:
            try:
                popup.ids.chooser.path = app.initial_dir
            except Exception:
                pass
        popup.open()

    def play(self):
        if not self.can_play:
            info_popup("Brak pliku gry", "Najpierw wskaż plik .exe gry.")
            return
        try:
            p = Path(self.game_path)
            subprocess.Popen([str(p)], cwd=str(p.parent))
        except Exception as e:
            info_popup("Błąd uruchamiania", f"Nie udało się uruchomić gry.\n{e}")


class WuwaLauncherApp(App):
    title = APP_TITLE
    initial_dir = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cfg = load_config()

    def build(self):
        # Załaduj KV z pliku lub wbudowany minimalny layout
        if KV_FILE.exists():
            Builder.load_file(str(KV_FILE))
        else:
            Builder.load_string(
                """
<LauncherRoot>:
    orientation: 'vertical'
    padding: '16dp'
    spacing: '12dp'
    Button:
        text: 'Graj'
        font_size: '20sp'
        size_hint_y: None
        height: '56dp'
        disabled: not root.can_play
        on_release: root.play()
    Label:
        text: root.status_text
        size_hint_y: None
        height: self.texture_size[1] + dp(8)
    Button:
        text: 'Wybierz plik gry…'
        size_hint_y: None
        height: '40dp'
        on_release: root.open_file_dialog()

<FileChooserPopup@Popup>:
    title: 'Wskaż plik wykonywalny gry'
    size_hint: 0.9, 0.9
    auto_dismiss: False
    BoxLayout:
        orientation: 'vertical'
        FileChooserListView:
            id: chooser
            filters: ['*.exe', '*.*']
        BoxLayout:
            size_hint_y: None
            height: '48dp'
            spacing: '8dp'
            padding: '8dp'
            Button:
                text: 'Anuluj'
                on_release: root.dismiss()
            Button:
                text: 'Wybierz'
                on_release: app.on_file_chosen(chooser.selection and chooser.selection[0] or '', root)
                """
            )

        # Ustaw początkowy katalog na katalog gry lub domowy
        path = self.cfg.get("game_path")
        if path:
            p = Path(path)
            if p.exists():
                self.initial_dir = str(p.parent)
        if not self.initial_dir:
            self.initial_dir = str(Path.home())

        root = LauncherRoot()
        if path:
            root.game_path = path
            root.refresh_state()
        return root

    def on_file_chosen(self, path: str, popup):
        try:
            popup.dismiss()
        except Exception:
            pass
        if not path:
            return
        p = Path(path)
        self.initial_dir = str(p.parent)
        self.cfg["game_path"] = str(p)
        try:
            save_config(self.cfg)
        except Exception as e:
            info_popup("Błąd zapisu", f"Nie udało się zapisać config.json\n{e}")
        root: LauncherRoot = self.root
        root.game_path = str(p)
        root.refresh_state()

    def open_native_dialog(self) -> str:
        """Otwórz natywne okno wyboru pliku w Windows przez tkinter.
        Zwraca wybraną ścieżkę lub pusty string.
        """
        if sys.platform != "win32":
            return ""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            try:
                root.attributes('-topmost', True)
            except Exception:
                pass
            path = filedialog.askopenfilename(
                title="Wskaż plik wykonywalny gry",
                initialdir=self.initial_dir or str(Path.home()),
                filetypes=(("Pliki EXE", "*.exe"), ("Wszystkie pliki", "*.*")),
            )
            try:
                root.destroy()
            except Exception:
                pass
            return path or ""
        except Exception as e:
            info_popup("Błąd okna systemowego", f"Nie udało się otworzyć systemowego okna wyboru pliku.\n{e}")
            return ""


def main():
    WuwaLauncherApp().run()


if __name__ == "__main__":
    main()
