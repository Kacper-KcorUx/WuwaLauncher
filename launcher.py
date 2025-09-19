from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

import shutil

try:
    from kivy.animation import Animation
    from kivy.app import App
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
    from kivy.uix.behaviors import ButtonBehavior
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.screenmanager import NoTransition, ScreenManager
    from kivy.uix.widget import Widget
    from kivy.core.image import Image as CoreImage
    from kivy.graphics import Color, Rectangle
    from kivy.core.window import Window
except Exception as exc:  # pragma: no cover - import-time helper
    missing = "kivy" if isinstance(exc, ModuleNotFoundError) else None
    print(
        "Nie znaleziono biblioteki Kivy. Zainstaluj zaleznosci i sproboj ponownie.\n"
        "Polecenie: pip install -r requirements.txt\n\nSzczegoly:",
        exc,
        file=sys.stderr,
    )
    if __name__ == "__main__":
        sys.exit(1)


APP_TITLE = "Wuthering Waves Launcher"
APP_ID = "WutheringWavesLauncher"
IS_FROZEN = getattr(sys, "frozen", False)
APP_ROOT = Path(sys.executable).resolve().parent if IS_FROZEN else Path(__file__).resolve().parent
BASE_PATH = Path(getattr(sys, "_MEIPASS", APP_ROOT))
KV_FILE = BASE_PATH / "launcher.kv"
ASSETS_DIR = BASE_PATH / "assets"
LANG_DIR = ASSETS_DIR / "lang"
DEFAULT_ASSETS_UI_DIR = ASSETS_DIR / "ui_assets"
CONFIG_DIR = APP_ROOT
CONFIG_FILE = CONFIG_DIR / "config.json"
CONFIG_FALLBACKS: tuple[Path, ...] = (BASE_PATH / "config.json",)
USER_DATA_DIR = APP_ROOT / "user_data"
USER_ASSETS_DIR = USER_DATA_DIR / "assets"
UI_ASSETS_DIR = USER_ASSETS_DIR / "ui_assets"
BACKGROUND_BASENAME = "background"
DEFAULT_LANG = "pl_PL"
FALLBACK_LANG = "en_US"


@dataclass(frozen=True)
class MenuEntry:
    icon: str
    label_key: str
    screen: str


MENU_ENTRIES: tuple[MenuEntry, ...] = (
    MenuEntry("H", "menu.home", "home"),
    MenuEntry("L", "menu.library", "library"),
    MenuEntry("S", "menu.store", "store"),
    MenuEntry("U", "menu.settings", "settings"),
)


KV_FALLBACK = """
#:import NoTransition kivy.uix.screenmanager.NoTransition
<Sidebar>:
    menu_container: menu_box
    orientation: 'vertical'
    size_hint: None, None
    padding: [dp(8), dp(16), dp(8), dp(16)]
    spacing: dp(8)
    height: root.parent.height - dp(32) if root.parent else self.height
    width: self.width
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.45
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12), dp(12), dp(12), dp(12)]
    AnchorLayout:
        anchor_x: 'left'
        anchor_y: 'top'
        size_hint: 1, 1
        BoxLayout:
            id: menu_box
            orientation: 'vertical'
            size_hint: 1, None
            height: self.minimum_height
            spacing: dp(8)

<SidebarButton>:
    orientation: 'horizontal'
    padding: [dp(12), 0, dp(12), 0]
    spacing: dp(12)
    size_hint_y: None
    height: dp(48)
    canvas.before:
        Color:
            rgba: (0.25, 0.28, 0.35, 0.6) if root.sidebar and root.sidebar.active_screen == root.screen_name else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(8), dp(8), dp(8), dp(8)]
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
    sidebar: sidebar
    content_manager: content_sm
    BoxLayout:
        id: content_container
        orientation: 'vertical'
        size_hint: 1, 1
        padding: [root.content_padding_left, dp(16), dp(16), dp(16)]
        spacing: dp(16)
        canvas.before:
            Color:
                rgba: 0, 0, 0, 0
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
                    Widget:
                    BoxLayout:
                        size_hint_y: None
                        height: dp(96)
                        padding: [0, dp(16), dp(16), dp(16)]
                        spacing: dp(16)
                        Widget:
                        Button:
                            id: play_button
                            text: app.translate('button.play') if app else 'Play'
                            size_hint: None, None
                            size: dp(72), dp(72)
                            font_size: '20sp'
                            on_release: app.root.play() if app.root else None
            Screen:
                name: 'library'
                BoxLayout:
                    orientation: 'vertical'
                    padding: [0, dp(16), dp(16), dp(16)]
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
                    padding: [0, dp(16), dp(16), dp(16)]
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
                    padding: [dp(16), dp(16), dp(16), dp(16)]
                    spacing: dp(12)
                    Label:
                        id: game_dir_label
                        text: app.translate('settings.game_dir_label') if app else 'Game directory'
                        size_hint_y: None
                        height: self.texture_size[1] + dp(12)
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.width, None
                    BoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(12)
                        Label:
                            id: game_dir_value
                            text: app.root.game_dir if app and app.root and app.root.game_dir else (app.translate('status.not_set') if app else 'Game directory: not set')
                            size_hint_x: 1
                            halign: 'left'
                            valign: 'middle'
                            text_size: self.width, None
                        Button:
                            id: choose_button
                            text: app.translate('settings.select_folder') if app else 'Select folder'
                            size_hint: None, None
                            size: dp(160), dp(44)
                            on_release: app.root.open_file_dialog() if app.root else None
                    Button:
                        id: background_button
                        text: app.translate('settings.change_background') if app else 'Change background'
                        size_hint: None, None
                        size: dp(200), dp(44)
                        on_release: app.select_background() if app else None
                    Label:
                        id: language_label
                        text: app.translate('settings.language_label') if app else 'Language'
                        size_hint_y: None
                        height: self.texture_size[1] + dp(12)
                        halign: 'left'
                        valign: 'middle'
                        text_size: self.width, None
                    Spinner:
                        id: language_spinner
                        size_hint: None, None
                        size: dp(220), dp(44)
                        values: []
                        on_text: app.on_language_selected(self.text) if app else None
                    Widget:
    Sidebar:
        id: sidebar
        pos: dp(16), dp(16)
        size_hint: None, None
        height: root.height - dp(32)
"""



def load_config(
    path: Path = CONFIG_FILE,
    fallbacks: Sequence[Path] = CONFIG_FALLBACKS,
) -> tuple[dict, bool]:
    primary_exists = path.exists()
    candidates: list[tuple[Path, bool]] = [(path, False)]
    for fallback in fallbacks:
        if fallback and fallback != path:
            candidates.append((fallback, True))
    for candidate, needs_save in candidates:
        if not candidate.exists():
            continue
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            continue
        return data, needs_save
    return {}, not primary_exists
def save_config(cfg: dict, path: Path = CONFIG_FILE) -> None:
    path = path.expanduser()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


def info_popup(title: str, message: str) -> None:
    Popup(
        title=title,
        content=Label(text=message, padding=(dp(12), dp(12))),
        size_hint=(0.6, 0.35),
        auto_dismiss=True,
    ).open()


class HoverBehavior:
    """Mixin that toggles a boolean when the pointer enters or leaves the widget."""

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

    def on_enter(self):  # pragma: no cover - hook for subclasses
        pass

    def on_leave(self):  # pragma: no cover - hook for subclasses
        pass


class SidebarButton(ButtonBehavior, BoxLayout):
    sidebar = ObjectProperty(None, rebind=True)
    icon_text = StringProperty("")
    text_label = StringProperty("")
    label_key = StringProperty("")
    screen_name = StringProperty("home")

    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", **kwargs)

    def on_release(self):
        if self.sidebar:
            self.sidebar.select(self.screen_name)


class Sidebar(HoverBehavior, BoxLayout):
    expanded_width = NumericProperty(dp(220))
    collapsed_width = NumericProperty(dp(72))
    label_width = NumericProperty(0)
    labels_opacity = NumericProperty(0)
    active_screen = StringProperty("home")
    show_labels = BooleanProperty(False)
    menu_container = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.width = self.collapsed_width
        self._callback: Callable[[str], None] | None = None
        self._buttons: list[SidebarButton] = []

    def on_kv_post(self, base_widget):
        self.width = self.collapsed_width
        self.label_width = 0
        self.labels_opacity = 0
        self.show_labels = False

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

    def populate(self, entries: Sequence[MenuEntry], callback: Callable[[str], None]) -> None:
        self._callback = callback
        container = self.menu_container
        if container is None:
            return
        container.clear_widgets()
        self._buttons = []
        app = App.get_running_app()
        for entry in entries:
            button = SidebarButton(
                sidebar=self,
                icon_text=entry.icon,
                label_key=entry.label_key,
                screen_name=entry.screen,
            )
            if app:
                button.text_label = app.translate(entry.label_key)
            else:
                button.text_label = entry.label_key
            container.add_widget(button)
            self._buttons.append(button)
        container.add_widget(Widget(size_hint_y=1))

    def update_labels(self):
        app = App.get_running_app()
        if not app:
            return
        for button in self._buttons:
            button.text_label = app.translate(button.label_key)

    def select(self, screen_name: str, dispatch: bool = True) -> None:
        self.active_screen = screen_name
        if dispatch and self._callback:
            self._callback(screen_name)


class LauncherRoot(FloatLayout):
    sidebar = ObjectProperty(None)
    content_manager = ObjectProperty(None)
    game_dir = StringProperty("")
    can_play = BooleanProperty(False)
    status_text = StringProperty("Game directory: not set")
    current_screen = StringProperty("home")
    content_padding_left = NumericProperty(dp(16) + dp(72))

    def __init__(self, **kwargs):
        self._bg_rect = None
        self._bg_color = None
        self._background_source: str | None = None
        super().__init__(**kwargs)
        self._ensure_background_canvas()

    def on_kv_post(self, base_widget):
        self.bind(can_play=self._sync_play_button, status_text=self._sync_status_label)
        if self.sidebar:
            self.sidebar.populate(MENU_ENTRIES, self.switch_to)
            self.sidebar.select(self.current_screen, dispatch=False)
            self.content_padding_left = dp(16) + self.sidebar.collapsed_width
        self.apply_translations()

    def refresh_state(self):
        app = App.get_running_app()
        dir_path = Path(self.game_dir).expanduser() if self.game_dir else None
        exe_path = dir_path / "Wuthering Waves.exe" if dir_path else None
        exists = bool(dir_path and dir_path.exists() and exe_path and exe_path.exists())
        self.can_play = exists
        if app:
            if dir_path and dir_path.exists():
                self.status_text = app.translate("status.set", path=str(dir_path))
            else:
                self.status_text = app.translate("status.not_set")
        else:
            if dir_path:
                self.status_text = f"Game directory: {dir_path}"
            else:
                self.status_text = "Game directory: not set"
        self._sync_play_button()
        self._sync_status_label()
        self._sync_game_dir_value()

    def _sync_play_button(self, *_):
        button = self.ids.get("play_button")
        if button:
            button.disabled = not self.can_play

    def _sync_status_label(self, *_):
        label = self.ids.get("status_label")
        if label:
            label.text = self.status_text

    def _sync_game_dir_value(self, *_):
        label = self.ids.get("game_dir_value")
        if label:
            label.text = self.status_text

    def _ensure_background_canvas(self):
        if self._bg_rect is None or self._bg_color is None:
            with self.canvas.before:
                self._bg_color = Color(0.11, 0.11, 0.13, 1)
                self._bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self._update_background_rect, size=self._update_background_rect)

    def _update_background_rect(self, *_):
        if self._bg_rect is not None:
            self._bg_rect.pos = self.pos
            self._bg_rect.size = self.size

    def update_background(self, path: str | Path | None):
        self._ensure_background_canvas()
        source = None
        if path:
            candidate = Path(path) if not isinstance(path, Path) else path
            if candidate.exists():
                try:
                    texture = CoreImage(str(candidate)).texture
                    source = str(candidate)
                    self._bg_rect.texture = texture
                    self._bg_color.rgba = (1, 1, 1, 1)
                except Exception:
                    source = None
        if not source and self._bg_rect is not None:
            self._bg_rect.texture = None
            if self._bg_color is not None:
                self._bg_color.rgba = (0.11, 0.11, 0.13, 1)
        self._background_source = source

    def apply_translations(self):
        app = App.get_running_app()
        if not app:
            return
        self.refresh_state()
        choose_btn = self.ids.get("choose_button")
        if choose_btn:
            choose_btn.text = app.translate("settings.select_folder")
        play_btn = self.ids.get("play_button")
        if play_btn:
            play_btn.text = app.translate("button.play")
        game_dir_label = self.ids.get("game_dir_label")
        if game_dir_label:
            game_dir_label.text = app.translate("settings.game_dir_label")
        language_label = self.ids.get("language_label")
        if language_label:
            language_label.text = app.translate("settings.language_label")
        background_button = self.ids.get("background_button")
        if background_button:
            background_button.text = app.translate("settings.change_background")
        spinner = self.ids.get("language_spinner")
        if spinner:
            values = [app.language_display_for(code) for code in app.available_languages]
            spinner.values = values
            spinner.text = app.language_display_for(app.current_language)
        if self.sidebar:
            self.sidebar.update_labels()
        self.update_background(app.background_path())
        self._sync_game_dir_value()

    def open_file_dialog(self):
        app = App.get_running_app()
        if sys.platform != "win32" or not hasattr(app, "open_directory_dialog"):
            info_popup(
                app.translate("popup.file_dialog.title") if app else "Unsupported",
                app.translate("popup.file_dialog.unsupported") if app else "Unsupported",
            )
            return
        selected = app.open_directory_dialog() if app else ''
        if selected:
            app.on_file_chosen(selected, None)

    def play(self):
        app = App.get_running_app()
        if not self.can_play:
            info_popup(
                app.translate("popup.no_game_file.title") if app else "Game File Missing",
                app.translate("popup.no_game_file.message") if app else "Select the game directory first.",
            )
            return
        try:
            dir_path = Path(self.game_dir)
            exe_path = dir_path / "Wuthering Waves.exe"
            subprocess.Popen([str(exe_path)], cwd=str(dir_path))
        except Exception as exc:
            info_popup(
                app.translate("popup.launch_error.title") if app else "Launch Error",
                app.translate("popup.launch_error.message", error=exc) if app else f"Failed to launch the game.\n{exc}",
            )

    def switch_to(self, screen_name: str) -> None:
        manager: ScreenManager | None = self.content_manager
        if manager and screen_name in manager.screen_names:
            manager.transition = NoTransition()
            manager.current = screen_name
        self.current_screen = screen_name
        if self.sidebar and self.sidebar.active_screen != screen_name:
            self.sidebar.select(screen_name, dispatch=False)
class WuwaLauncherApp(App):
    title = APP_TITLE
    initial_dir = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        USER_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        UI_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        self.cfg, needs_save = load_config()
        legacy_path = self.cfg.pop("game_path", None)
        converted = legacy_path is not None
        if legacy_path and "game_dir" not in self.cfg:
            legacy = Path(legacy_path)
            game_dir = legacy.parent if legacy.suffix else legacy
            self.cfg["game_dir"] = str(game_dir)
            converted = True
        self.available_languages = ("pl_PL", "en_US")
        lang = self.cfg.get("language", DEFAULT_LANG)
        if lang not in self.available_languages:
            lang = DEFAULT_LANG
        self.current_language = lang
        self._fallback_translations = self._load_language_file(FALLBACK_LANG)
        self.translations: dict[str, str] = {}
        self.language_display_map: dict[str, str] = {}
        self.language_display_lookup: dict[str, str] = {}
        self.set_language(self.current_language, persist=False)
        defaults_applied = False
        if self.cfg.get("language") != self.current_language:
            self.cfg["language"] = self.current_language
            defaults_applied = True
        if "game_dir" not in self.cfg:
            self.cfg["game_dir"] = ""
            defaults_applied = True
        if "background_image" not in self.cfg:
            self.cfg["background_image"] = ""
            defaults_applied = True
        if "window_size" not in self.cfg:
            self.cfg["window_size"] = [Window.size[0], Window.size[1]]
            defaults_applied = True
        if "window_position" not in self.cfg:
            self.cfg["window_position"] = [Window.left, Window.top]
            defaults_applied = True
        if converted or needs_save or defaults_applied:
            try:
                save_config(self.cfg)
            except Exception:
                pass

    def build(self):
        Window.clearcolor = (0, 0, 0, 0)
        if KV_FILE.exists():
            Builder.load_file(str(KV_FILE))
        else:
            Builder.load_string(KV_FALLBACK)
        self._prepare_initial_dir()
        size = self.cfg.get("window_size")
        if size and isinstance(size, (list, tuple)) and len(size) == 2:
            try:
                Window.size = (float(size[0]), float(size[1]))
            except Exception:
                pass
        position = self.cfg.get("window_position")
        if position and isinstance(position, (list, tuple)) and len(position) == 2:
            try:
                Window.left = int(position[0])
                Window.top = int(position[1])
            except Exception:
                pass
        Window.bind(on_resize=self._on_window_resize, on_move=self._on_window_move)
        root = LauncherRoot()
        root.game_dir = self.cfg.get("game_dir", "")
        root.apply_translations()
        root.switch_to("home")
        root.update_background(self.background_path())
        return root

    def _prepare_initial_dir(self) -> None:
        path = self.cfg.get("game_dir")
        if path:
            candidate = Path(path)
            if candidate.exists():
                self.initial_dir = str(candidate)
                return
        self.initial_dir = str(Path.home())

    def _load_language_file(self, code: str) -> dict[str, str]:
        file = LANG_DIR / code / "messages.json"
        if not file.exists():
            return {}
        try:
            return json.loads(file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _refresh_language_maps(self):
        self.language_display_map = {}
        self.language_display_lookup = {}
        for code in self.available_languages:
            display = self.translate(f"settings.language.{code}")
            self.language_display_map[code] = display
            self.language_display_lookup[display] = code

    def language_display_for(self, code: str) -> str:
        return self.language_display_map.get(code, code)

    def set_language(self, code: str, persist: bool = True) -> None:
        normalized = code if code in self.available_languages else FALLBACK_LANG
        translations = self._load_language_file(normalized)
        if not translations:
            normalized = FALLBACK_LANG
            translations = self._load_language_file(normalized)
        self.current_language = normalized
        self.translations = translations
        self._refresh_language_maps()
        if persist:
            self.cfg["language"] = normalized
            try:
                save_config(self.cfg)
            except Exception as exc:
                info_popup(
                    self.translate("popup.save_error.title"),
                    self.translate("popup.save_error.message", error=exc),
                )
        if self.root:
            self.root.apply_translations()

    def translate(self, key: str, **kwargs) -> str:
        template = self.translations.get(key) or self._fallback_translations.get(key) or key
        try:
            return template.format(**kwargs)
        except Exception:
            return template

    def on_language_selected(self, display_name: str) -> None:
        code = self.language_display_lookup.get(display_name)
        if not code or code == self.current_language:
            return
        self.set_language(code)

    def on_file_chosen(self, path: str, popup):
        try:
            if popup:
                popup.dismiss()
        except Exception:
            pass
        if not path:
            return
        selected = Path(path)
        if selected.is_file():
            selected = selected.parent
        self.initial_dir = str(selected)
        self.cfg["game_dir"] = str(selected)
        try:
            save_config(self.cfg)
        except Exception as exc:
            info_popup(
                self.translate("popup.save_error.title"),
                self.translate("popup.save_error.message", error=exc),
            )
        root: LauncherRoot = self.root
        root.game_dir = str(selected)
        root.apply_translations()

    def open_directory_dialog(self) -> str:
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
            path = filedialog.askdirectory(
                title=self.translate("settings.select_folder"),
                initialdir=self.initial_dir or str(Path.home()),
            )
            try:
                root.destroy()
            except Exception:
                pass
            return path or ""
        except Exception as exc:
            info_popup(
                self.translate("popup.file_dialog.error.title"),
                self.translate("popup.file_dialog.error.message", error=exc),
            )
            return ""

    def open_image_dialog(self) -> str:
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
                title=self.translate("settings.change_background"),
                initialdir=self.initial_dir or str(Path.home()),
                filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")),
            )
            try:
                root.destroy()
            except Exception:
                pass
            return path or ""
        except Exception as exc:
            info_popup(
                self.translate("popup.file_dialog.error.title"),
                self.translate("popup.file_dialog.error.message", error=exc),
            )
            return ""

    def select_background(self) -> None:
        path = self.open_image_dialog()
        if not path:
            return
        src = Path(path)
        dest = UI_ASSETS_DIR / f"{BACKGROUND_BASENAME}{src.suffix.lower()}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        for existing in dest.parent.glob(f"{BACKGROUND_BASENAME}.*"):
            try:
                existing.unlink()
            except Exception:
                pass
        try:
            shutil.copy2(src, dest)
            self.cfg["background_image"] = str(dest)
            self.initial_dir = str(src.parent)
            self._save_config_silent()
            if self.root:
                self.root.update_background(dest)
        except Exception as exc:
            info_popup(
                self.translate("popup.save_error.title"),
                self.translate("popup.save_error.message", error=exc),
            )

    def _save_config_silent(self):
        try:
            save_config(self.cfg)
        except Exception:
            pass

    def _on_window_resize(self, window, width, height):
        self.cfg["window_size"] = [int(width), int(height)]
        self._save_config_silent()

    def _on_window_move(self, window, *args):
        try:
            if len(args) >= 2:
                x, y = args[0], args[1]
            else:
                x, y = window.left, window.top
            self.cfg["window_position"] = [int(x), int(y)]
            self._save_config_silent()
        except Exception:
            pass

    def background_path(self) -> Path | None:
        configured = self.cfg.get("background_image")
        if configured:
            candidate = Path(configured).expanduser()
            if not candidate.is_absolute():
                candidate = UI_ASSETS_DIR / candidate
            if candidate.exists():
                return candidate
        user_matches = sorted(UI_ASSETS_DIR.glob(f"{BACKGROUND_BASENAME}.*"))
        if user_matches:
            return user_matches[0]
        default_matches = sorted(DEFAULT_ASSETS_UI_DIR.glob(f"{BACKGROUND_BASENAME}.*"))
        return default_matches[0] if default_matches else None



    def on_stop(self):
        try:
            save_config(self.cfg)
        except Exception:
            pass

def main():
    WuwaLauncherApp().run()


if __name__ == "__main__":
    main()


