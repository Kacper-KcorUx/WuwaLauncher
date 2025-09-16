from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

try:
    from kivy.animation import Animation
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.screenmanager import ScreenManager, NoTransition
    from kivy.core.window import Window
except Exception as e:  # pragma: no cover - import-time helper
    missing = "kivy" if isinstance(e, ModuleNotFoundError) else None
    print(
        "Nie znaleziono biblioteki Kivy. Zainstaluj zaleznosci i sproboj ponownie.\n"
        "Polecenie: pip install -r requirements.txt\n\nSzczegoly:",
        e,
        file=sys.stderr,
    )
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


class HoverBehavior:
    """Mixin that toggles hovered state when the pointer enters or leaves the widget."""

    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type("on_enter")
        self.register_event_type("on_leave")
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            return
        self.hovered = inside
        if inside:
            self.dispatch("on_enter")
        else:
            self.dispatch("on_leave")

    def on_enter(self):
        pass

    def on_leave(self):
        pass


class Sidebar(HoverBehavior, BoxLayout):
    expanded_width = NumericProperty(dp(220))
    collapsed_width = NumericProperty(dp(72))
    label_width = NumericProperty(0)
    labels_opacity = NumericProperty(0)
    active_screen = StringProperty("home")
    show_labels = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = self.collapsed_width

    def on_kv_post(self, base_widget):
        self.width = self.collapsed_width
        self.label_width = 0
        self.labels_opacity = 0

    def on_hovered(self, instance, value):
        self.show_labels = bool(value)
        target_width = self.expanded_width if value else self.collapsed_width
        target_label_width = max(0, self.expanded_width - self.collapsed_width) if value else 0
        target_opacity = 1 if value else 0
        Animation.cancel_all(self, "width", "label_width", "labels_opacity")
        Animation(
            width=target_width,
            label_width=target_label_width,
            labels_opacity=target_opacity,
            duration=0.25,
            t="out_quad",
        ).start(self)

    def activate(self, screen_name: str) -> None:
        self.active_screen = screen_name
        parent = self.parent
        if parent and hasattr(parent, "switch_to"):
            parent.switch_to(screen_name)


class LauncherRoot(FloatLayout):
    game_path = StringProperty("")
    can_play = BooleanProperty(False)
    status_text = StringProperty("Plik gry: nie ustawiono")
    current_screen = StringProperty("home")
    content_padding_left = NumericProperty(dp(16) + dp(72))

    def on_kv_post(self, base_widget):
        sidebar: Sidebar | None = self.ids.get("sidebar")
        if sidebar:
            self.content_padding_left = dp(16) + sidebar.collapsed_width

    def refresh_state(self):
        p = Path(self.game_path) if self.game_path else None
        ok = bool(p and p.exists())
        self.can_play = ok
        self.status_text = f"Plik gry: {p}" if ok else "Plik gry: nie ustawiono"

    def open_file_dialog(self):
        app = App.get_running_app()
        if sys.platform != "win32" or not hasattr(app, "open_native_dialog"):
            info_popup("Brak wsparcia", "System obslugiwany tylko przez natywny dialog Windows.")
            return
        path = app.open_native_dialog()
        if path:
            app.on_file_chosen(path, None)

    def play(self):
        if not self.can_play:
            info_popup("Brak pliku gry", "Najpierw wskaz plik .exe gry.")
            return
        try:
            p = Path(self.game_path)
            subprocess.Popen([str(p)], cwd=str(p.parent))
        except Exception as e:
            info_popup("Blad uruchamiania", f"Nie udalo sie uruchomic gry.\n{e}")

    def switch_to(self, screen_name: str) -> None:
        sm: ScreenManager | None = self.ids.get("content_sm")
        if sm and screen_name in sm.screen_names:
            sm.transition = NoTransition()
            sm.current = screen_name
        self.current_screen = screen_name
        sidebar: Sidebar | None = self.ids.get("sidebar")
        if sidebar:
            sidebar.active_screen = screen_name


class WuwaLauncherApp(App):
    title = APP_TITLE
    initial_dir = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cfg = load_config()

    def build(self):
        Window.clearcolor = (0, 0, 0, 0)
        if KV_FILE.exists():
            Builder.load_file(str(KV_FILE))
        else:
            Builder.load_string(
                """
#:import NoTransition kivy.uix.screenmanager.NoTransition
<Sidebar>:
    orientation: 'vertical'
    size_hint: None, None
    padding: [dp(8), dp(16), dp(8), dp(16)]
    spacing: dp(8)
    height: root.parent.height - dp(32) if root.parent else self.height
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.09, 0.72
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12), dp(12), dp(12), dp(12)]

<SidebarItem@Button>:
    sidebar: None
    icon_text: ''
    text_label: ''
    screen_name: ''
    size_hint_y: None
    height: dp(48)
    background_normal: ''
    background_down: ''
    background_color: 0, 0, 0, 0
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: (0.25, 0.28, 0.35, 0.6) if root.sidebar and root.sidebar.active_screen == root.screen_name else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8), dp(8), dp(8), dp(8)]
    BoxLayout:
        orientation: 'horizontal'
        spacing: dp(12)
        padding: [dp(12), 0, dp(12), 0]
        size_hint: 1, 1
        Label:
            text: root.icon_text
            size_hint_x: None
            width: dp(24)
            halign: 'center'
            valign: 'middle'
            text_size: self.size
        Label:
            text: root.sidebar and root.sidebar.show_labels and root.text_label or ''
            opacity: root.sidebar.labels_opacity if root.sidebar else 0
            size_hint_x: None
            width: root.sidebar.label_width if root.sidebar else 0
            halign: 'left'
            valign: 'middle'
            text_size: self.size
            shorten: True
            shorten_from: 'right'

<LauncherRoot>:
    canvas.before:
        Color:
            rgba: 0.11, 0.11, 0.13, 0.6
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        id: content_container
        orientation: 'vertical'
        size_hint: 1, 1
        padding: [root.content_padding_left, dp(16), dp(16), dp(16)]
        spacing: dp(16)
        canvas.before:
            Color:
                rgba: 0.15, 0.15, 0.18, 0.82
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(16), dp(16), dp(16), dp(16)]
        ScreenManager:
            id: content_sm
            transition: NoTransition()
            Screen:
                name: 'home'
                BoxLayout:
                    orientation: 'vertical'
                    spacing: dp(16)
                    padding: [0, 0, 0, dp(8)]
                    Label:
                        text: app.root.status_text if app.root else ''
                        size_hint_y: None
                        height: self.texture_size[1] + dp(12)
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.width, None
                    Widget:
                    BoxLayout:
                        size_hint_y: None
                        height: dp(96)
                        padding: [0, dp(16), dp(16), dp(16)]
                        spacing: dp(16)
                        Widget:
                        Button:
                            text: 'Plik'
                            size_hint: None, None
                            size: dp(56), dp(56)
                            on_release: app.root.open_file_dialog() if app.root else None
                        Button:
                            text: 'Graj'
                            size_hint: None, None
                            size: dp(72), dp(72)
                            font_size: '20sp'
                            disabled: not app.root.can_play if app.root else True
                            on_release: app.root.play() if app.root else None
            Screen:
                name: 'library'
                BoxLayout:
                    orientation: 'vertical'
                    padding: [0, dp(16), 0, dp(16)]
                    spacing: dp(12)
                    Label:
                        text: 'Biblioteka w przygotowaniu'
                        size_hint_y: None
                        height: self.texture_size[1] + dp(12)
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.width, None
                    Widget:
            Screen:
                name: 'store'
                BoxLayout:
                    orientation: 'vertical'
                    padding: [0, dp(16), 0, dp(16)]
                    spacing: dp(12)
                    Label:
                        text: 'Sklep w przygotowaniu'
                        size_hint_y: None
                        height: self.texture_size[1] + dp(12)
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.width, None
                    Widget:
            Screen:
                name: 'settings'
                BoxLayout:
                    orientation: 'vertical'
                    padding: [0, dp(16), 0, dp(16)]
                    spacing: dp(12)
                    Label:
                        text: 'Ustawienia w przygotowaniu'
                        size_hint_y: None
                        height: self.texture_size[1] + dp(12)
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.width, None
                    Widget:
    Sidebar:
        id: sidebar
        pos: dp(16), dp(16)
        size_hint: None, None
        height: root.height - dp(32)
        AnchorLayout:
            anchor_x: 'left'
            anchor_y: 'top'
            size_hint: 1, 1
            padding: 0
            BoxLayout:
                orientation: 'vertical'
                size_hint: 1, None
                height: self.minimum_height
                spacing: dp(8)
                SidebarItem:
                    sidebar: root.ids.sidebar
                    icon_text: 'H'
                    text_label: 'Strona glowna'
                    screen_name: 'home'
                    on_release: root.ids.sidebar.activate('home')
                SidebarItem:
                    sidebar: root.ids.sidebar
                    icon_text: 'L'
                    text_label: 'Biblioteka'
                    screen_name: 'library'
                    on_release: root.ids.sidebar.activate('library')
                SidebarItem:
                    sidebar: root.ids.sidebar
                    icon_text: 'S'
                    text_label: 'Sklep'
                    screen_name: 'store'
                    on_release: root.ids.sidebar.activate('store')
                SidebarItem:
                    sidebar: root.ids.sidebar
                    icon_text: 'U'
                    text_label: 'Ustawienia'
                    screen_name: 'settings'
                    on_release: root.ids.sidebar.activate('settings')
                Widget:
                    size_hint_y: 1
"""
            )

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
            if popup:
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
            info_popup("Blad zapisu", f"Nie udalo sie zapisac config.json\n{e}")
        root: LauncherRoot = self.root
        root.game_path = str(p)
        root.refresh_state()

    def open_native_dialog(self) -> str:
        """Otworz natywne okno wyboru pliku w Windows przez tkinter."""
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
                title="Wskaz plik wykonywalny gry",
                initialdir=self.initial_dir or str(Path.home()),
                filetypes=(("Pliki EXE", "*.exe"), ("Wszystkie pliki", "*.*")),
            )
            try:
                root.destroy()
            except Exception:
                pass
            return path or ""
        except Exception as e:
            info_popup("Blad okna systemowego", f"Nie udalo sie otworzyc systemowego okna wyboru pliku.\n{e}")
            return ""


def main():
    WuwaLauncherApp().run()


if __name__ == "__main__":
    main()













