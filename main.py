"""
KivyMD tabanlı, Samsung One UI tasarımlı, pyjnius entegre P2P dosya gönder/al arayüzü.
Android uygulaması için, WakeLock ve WifiLock desteğiyle arka plan işlemlerinin sürdürülmesini sağlar.

Android APK üretimi için buildozer/python-for-android ile paketlenebilir.
requirements: kivy, kivymd, pillow, pyjnius
"""
from __future__ import annotations

import threading
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable, Optional

try:
    from jnius import autoclass, cast
    HAS_JNIUS = True
except ImportError:
    HAS_JNIUS = False

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.popup import MDPopup
from kivymd.uix.filechooser import MDFileManager
from kivymd.uix.textfield import MDTextField
from kivymd.uix.switch import MDSwitch
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.theme_cls import ThemeManager
from kivy.garden.filebrowser import FileBrowser

from p2p import send_file, receive_file, ensure_local


# Android native locks
class AndroidLocks:
    """Wrapper for Android WakeLock and WifiLock via pyjnius."""
    
    def __init__(self):
        self.wake_lock = None
        self.wifi_lock = None
        
        if HAS_JNIUS:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                
                # WakeLock
                PowerManager = autoclass('android.os.PowerManager')
                pm = activity.getSystemService('power')
                self.wake_lock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, 'P2P:WakeLock')
                
                # WifiLock
                WifiManager = autoclass('android.net.wifi.WifiManager')
                Context = autoclass('android.content.Context')
                wm = activity.getSystemService('wifi')
                self.wifi_lock = wm.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, 'P2P:WifiLock')
            except Exception as e:
                print(f"[!] Android locks başlatma hatası: {e}")
    
    def acquire(self) -> None:
        """Acquire both locks."""
        try:
            if self.wake_lock and not self.wake_lock.isHeld():
                self.wake_lock.acquire()
            if self.wifi_lock and not self.wifi_lock.isHeld():
                self.wifi_lock.acquire()
        except Exception as e:
            print(f"[!] Lock acquire hatası: {e}")
    
    def release(self) -> None:
        """Release both locks."""
        try:
            if self.wake_lock and self.wake_lock.isHeld():
                self.wake_lock.release()
            if self.wifi_lock and self.wifi_lock.isHeld():
                self.wifi_lock.release()
        except Exception as e:
            print(f"[!] Lock release hatası: {e}")


class LogWriter:
    """stdout'u MDApp log ekranına yönlendirmek için."""

    def __init__(self, append_fn: Callable[[str], None]):
        self.append_fn = append_fn

    def write(self, data: str) -> None:
        text = data.rstrip("\n")
        if text:
            self.append_fn(text)

    def flush(self) -> None:
        return


class P2PApp(MDApp):
    def build(self):
        Window.size = (360, 800)
        
        # Samsung One UI Color Palette
        self.theme_cls.primary_color = (0, 122/255, 254/255, 1)  # Samsung Blue (#007AFE)
        self.theme_cls.primary_hue = "500"
        self.theme_cls.accent_color = (0.13, 0.8, 0.45, 1)  # Green
        self.theme_cls.theme_style = "Light"
        
        self.mode = "send"
        self.android_locks = AndroidLocks()
        self._running = False
        self._file_manager = None
        
        # Main container
        root = MDBoxLayout(orientation="vertical", padding="16dp", spacing="8dp", size_hint=(1, 1))
        root.md_bg_color = (248/255, 249/255, 250/255, 1)  # Light Gray (#F8F9FA)
        
        # ===== HEADER =====
        header_card = MDCard(
            MDLabel(
                text="P2P Paylaş",
                font_style="H4",
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1),
                size_hint_y=None,
                height="80dp",
                padding="16dp",
                halign="left",
            ),
            size_hint_y=None,
            height="120dp",
            md_bg_color=(248/255, 249/255, 250/255, 1),
            radius=[24, 24, 24, 24],
            elevation="2dp",
            padding="16dp",
        )
        root.add_widget(header_card)
        
        # ===== MODE TOGGLE =====
        mode_card = MDCard(
            MDGridLayout(
                cols=2,
                spacing="12dp",
                size_hint_y=1,
                padding="8dp",
            ),
            size_hint_y=None,
            height="56dp",
            md_bg_color=(1, 1, 1, 1),
            radius=[24, 24, 24, 24],
            elevation="1dp",
        )
        
        mode_grid = mode_card.children[0]
        mode_label = MDLabel(
            text="GÖNDER",
            size_hint_x=0.5,
            theme_text_color="Custom",
            text_color=(0, 122/255, 254/255, 1),
            bold=True,
        )
        mode_switch = MDSwitch(
            size_hint_x=0.5,
            active=True,
        )
        mode_switch.bind(active=self.on_mode_toggle)
        self.mode_switch = mode_switch
        
        mode_grid.add_widget(mode_label)
        mode_grid.add_widget(mode_switch)
        root.add_widget(mode_card)
        
        # ===== SCOPE TOGGLE (LAN/WAN) =====
        scope_card = MDCard(
            MDGridLayout(
                cols=2,
                spacing="12dp",
                size_hint_y=1,
                padding="8dp",
            ),
            size_hint_y=None,
            height="56dp",
            md_bg_color=(1, 1, 1, 1),
            radius=[24, 24, 24, 24],
            elevation="1dp",
        )
        
        scope_grid = scope_card.children[0]
        scope_label = MDLabel(
            text="SADECe YEREL AĞ",
            size_hint_x=0.5,
            theme_text_color="Custom",
            text_color=(0, 0, 0, 0.6),
            font_style="Caption",
        )
        scope_switch = MDSwitch(
            size_hint_x=0.5,
            active=True,
        )
        self.scope_switch = scope_switch
        
        scope_grid.add_widget(scope_label)
        scope_grid.add_widget(scope_switch)
        root.add_widget(scope_card)
        
        # ===== INPUT FIELDS =====
        scroll = MDScrollView(size_hint=(1, 1))
        form = MDGridLayout(cols=1, spacing="12dp", size_hint_y=None, padding="8dp")
        form.bind(minimum_height=form.setter('height'))
        
        # PIN field
        self.pin_input = MDTextField(
            hint_text="PIN (6 rakam)",
            text="123456",
            mode="rectangle",
            size_hint_x=1,
            size_hint_y=None,
            height="48dp",
            input_filter="int",
            max_text_length=6,
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        form.add_widget(self.pin_input)
        
        # Port field
        self.port_input = MDTextField(
            hint_text="Port",
            text="5000",
            mode="rectangle",
            size_hint_x=1,
            size_hint_y=None,
            height="48dp",
            input_filter="int",
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        form.add_widget(self.port_input)
        
        # Chunk size field
        self.chunk_input = MDTextField(
            hint_text="Blok boyutu (bayt)",
            text="1048576",
            mode="rectangle",
            size_hint_x=1,
            size_hint_y=None,
            height="48dp",
            input_filter="int",
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        form.add_widget(self.chunk_input)
        
        # Host field (send mode)
        self.host_input = MDTextField(
            hint_text="Alıcı host (GÖNDER modu)",
            text="192.168.1.50",
            mode="rectangle",
            size_hint_x=1,
            size_hint_y=None,
            height="48dp",
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        form.add_widget(self.host_input)
        
        # File picker (send mode)
        file_row = MDBoxLayout(size_hint_y=None, height="48dp", spacing="8dp")
        self.file_input = MDTextField(
            hint_text="Gönderilecek dosya/klasör",
            mode="rectangle",
            size_hint_x=0.85,
            size_hint_y=1,
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        file_btn = MDRaisedButton(
            text="Seç",
            size_hint_x=0.15,
            size_hint_y=1,
            md_bg_color=(0, 122/255, 254/255, 1),
        )
        file_btn.bind(on_press=lambda _: self.show_file_picker(pick_dir=False))
        file_row.add_widget(self.file_input)
        file_row.add_widget(file_btn)
        form.add_widget(file_row)
        
        # Bind address field (receive mode)
        self.bind_input = MDTextField(
            hint_text="Dinlenecek adres (AL modu)",
            text="0.0.0.0",
            mode="rectangle",
            size_hint_x=1,
            size_hint_y=None,
            height="48dp",
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        form.add_widget(self.bind_input)
        
        # Output folder picker (receive mode)
        out_row = MDBoxLayout(size_hint_y=None, height="48dp", spacing="8dp")
        self.out_input = MDTextField(
            hint_text="Çıkış klasörü (AL modu)",
            mode="rectangle",
            size_hint_x=0.85,
            size_hint_y=1,
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        out_btn = MDRaisedButton(
            text="Seç",
            size_hint_x=0.15,
            size_hint_y=1,
            md_bg_color=(0, 122/255, 254/255, 1),
        )
        out_btn.bind(on_press=lambda _: self.show_file_picker(pick_dir=True))
        out_row.add_widget(self.out_input)
        out_row.add_widget(out_btn)
        form.add_widget(out_row)
        
        scroll.add_widget(form)
        root.add_widget(scroll)
        
        # ===== START BUTTON =====
        self.start_btn = MDRaisedButton(
            text="BAŞLAT",
            size_hint_y=None,
            height="48dp",
            md_bg_color=(0, 122/255, 254/255, 1),
        )
        self.start_btn.bind(on_press=lambda _: self.start_action())
        root.add_widget(self.start_btn)
        
        # ===== LOG AREA =====
        log_scroll = MDScrollView(size_hint=(1, None), height="150dp")
        self.log_label = MDLabel(
            text="İşlem kayıtları burada görünecek...",
            size_hint_y=None,
            theme_text_color="Custom",
            text_color=(0, 0, 0, 0.7),
            font_style="Caption",
        )
        self.log_label.bind(texture_size=self._update_log_height)
        log_scroll.add_widget(self.log_label)
        root.add_widget(log_scroll)
        
        self._toggle_visibility()
        return root
    
    def _update_log_height(self, *args):
        self.log_label.height = max(self.log_label.texture_size[1], 150)
        self.log_label.text_size = (self.log_label.width, None)
    
    def on_mode_toggle(self, _instance, value: bool):
        self.mode = "send" if value else "receive"
        self._toggle_visibility()
    
    def _toggle_visibility(self):
        send_mode = self.mode == "send"
        self.host_input.opacity = 1 if send_mode else 0
        self.file_input.opacity = 1 if send_mode else 0
        self.bind_input.opacity = 1 if not send_mode else 0
        self.out_input.opacity = 1 if not send_mode else 0
    
    def append_log(self, text: str) -> None:
        if not self.log_label.text.startswith("İşlem kayıtları"):
            self.log_label.text += f"\n{text}"
        else:
            self.log_label.text = text
    
    def show_file_picker(self, pick_dir: bool) -> None:
        """Show file/directory picker."""
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        
        content = BoxLayout(orientation='vertical')
        
        # Create file chooser
        file_chooser = FileChooserListView(
            dirselect=pick_dir,
            filters=['*'] if not pick_dir else None
        )
        content.add_widget(file_chooser)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.1, spacing='10dp')
        
        def on_select(*args):
            if file_chooser.selection:
                selected = file_chooser.selection[0]
                if pick_dir:
                    self.out_input.text = selected
                else:
                    self.file_input.text = selected
                popup.dismiss()
        
        def on_cancel(*args):
            popup.dismiss()
        
        select_btn = MDRaisedButton(text="Seç")
        select_btn.bind(on_press=on_select)
        cancel_btn = MDFlatButton(text="İptal")
        cancel_btn.bind(on_press=on_cancel)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Dosya Seç" if not pick_dir else "Klasör Seç", content=content, size_hint=(0.9, 0.9))
        popup.open()
    
    def start_action(self):
        if self._running:
            return
        
        try:
            port = int(self.port_input.text)
            chunk_size = int(self.chunk_input.text)
            if port <= 0 or port > 65535 or chunk_size <= 0:
                raise ValueError("Port ve blok boyutu geçersiz")
        except ValueError as e:
            self.append_log(f"[!] Hata: {e}")
            return
        
        pin = self.pin_input.text.strip()
        if not pin:
            self.append_log("[!] PIN boş olamaz.")
            return
        
        local_only = bool(self.scope_switch.active)
        
        if self.mode == "send":
            host = self.host_input.text.strip()
            file_path = Path(self.file_input.text)
            if not host:
                self.append_log("[!] Alıcı host gerekli.")
                return
            if not file_path.exists():
                self.append_log("[!] Gönderilecek dosya/klasör bulunamadı.")
                return
            if local_only:
                try:
                    ensure_local(host)
                except Exception as exc:
                    self.append_log(f"[!] {exc}")
                    return
            target_fn = lambda: send_file(host, port, pin, file_path, chunk_size)
        else:
            bind_addr = self.bind_input.text.strip() or "0.0.0.0"
            output_dir = Path(self.out_input.text or ".")
            if local_only:
                try:
                    ensure_local(bind_addr)
                except Exception as exc:
                    self.append_log(f"[!] {exc}")
                    return
            target_fn = lambda: receive_file(bind_addr, port, pin, output_dir, chunk_size)
        
        self._run_thread(target_fn)
    
    def _run_thread(self, target_fn):
        self._running = True
        self.start_btn.disabled = True
        writer = LogWriter(lambda t: Clock.schedule_once(lambda *_: self.append_log(t)))
        
        # Acquire Android locks
        self.android_locks.acquire()
        
        def runner():
            try:
                with redirect_stdout(writer):
                    target_fn()
                Clock.schedule_once(lambda *_: self.append_log("[✓] Tamamlandı."))
            except Exception as exc:
                Clock.schedule_once(lambda *_: self.append_log(f"[!] Hata: {exc}"))
            finally:
                self._running = False
                Clock.schedule_once(lambda *_: setattr(self.start_btn, "disabled", False))
                # Release Android locks
                self.android_locks.release()
        
        threading.Thread(target=runner, daemon=True).start()


def launch():
    P2PApp().run()


if __name__ == "__main__":
    launch()
