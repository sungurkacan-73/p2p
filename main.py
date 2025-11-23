"""
KivyMD tabanlı, sade P2P dosya gönder/al arayüzü.

requirements: kivy, kivymd, pillow
"""
from __future__ import annotations

import ipaddress
import threading
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable, Optional

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.tab import MDTabs, MDTabsBase

import p2p
from p2p import send_file, receive_file, ensure_local


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


class BaseTab(MDBoxLayout, MDTabsBase):
    """Shared helpers for tab content."""

    def __init__(self, app: "P2PApp", **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = "vertical"
        self.padding = "0dp"
        self.spacing = "8dp"

    def _input_row(self, hint: str, default: str = "", helper: str | None = None) -> MDTextField:
        field = MDTextField(
            hint_text=hint,
            text=default,
            mode="rectangle",
            size_hint_y=None,
            height="48dp",
            md_bg_color=(242/255, 242/255, 242/255, 1),
            helper_text=helper,
            helper_text_mode="persistent" if helper else "on_focus",
        )
        return field


class SendTab(BaseTab):
    title = "Gönder"

    def __init__(self, app: "P2PApp", **kwargs):
        super().__init__(app, **kwargs)

        scroll = MDScrollView(size_hint=(1, 1))
        form = MDGridLayout(cols=1, spacing="12dp", padding="4dp", size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.host_input = self._input_row("Alıcı host", "192.168.1.50")
        self.port_input = self._input_row("Port", "5000", helper="Boş bırakılırsa varsayılan 5000")
        self.port_input.input_filter = "int"
        self.chunk_input = self._input_row("Blok boyutu (bayt)", "1048576", helper="Boş bırakılırsa otomatik optimize edilir")
        self.chunk_input.input_filter = "int"

        file_row = MDBoxLayout(size_hint_y=None, height="48dp", spacing="8dp")
        self.file_input = MDTextField(
            hint_text="Gönderilecek dosya/klasör",
            mode="rectangle",
            size_hint_y=1,
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        file_btn = MDRaisedButton(
            text="Seç",
            size_hint_y=1,
            md_bg_color=(0, 122/255, 254/255, 1),
        )
        file_btn.bind(on_press=lambda *_: app.show_file_picker(pick_dir=False, target_field=self.file_input))
        file_row.add_widget(self.file_input)
        file_row.add_widget(file_btn)

        form.add_widget(self.host_input)
        form.add_widget(self.port_input)
        form.add_widget(self.chunk_input)
        form.add_widget(file_row)

        scroll.add_widget(form)
        self.add_widget(scroll)

        self.start_btn = MDRaisedButton(
            text="Gönder", size_hint_y=None, height="48dp", md_bg_color=(0, 122/255, 254/255, 1)
        )
        self.start_btn.bind(on_press=lambda *_: app.start_action("send"))
        self.add_widget(self.start_btn)


class ReceiveTab(BaseTab):
    title = "Al"

    def __init__(self, app: "P2PApp", **kwargs):
        super().__init__(app, **kwargs)

        scroll = MDScrollView(size_hint=(1, 1))
        form = MDGridLayout(cols=1, spacing="12dp", padding="4dp", size_hint_y=None)
        form.bind(minimum_height=form.setter("height"))

        self.bind_input = self._input_row("Dinlenecek adres", "0.0.0.0", helper="Boş ise tüm arayüzler")
        self.port_input = self._input_row("Port", "5000", helper="Boş bırakılırsa varsayılan 5000")
        self.port_input.input_filter = "int"
        self.chunk_input = self._input_row("Blok boyutu (bayt)", "1048576", helper="Boş bırakılırsa otomatik optimize edilir")
        self.chunk_input.input_filter = "int"

        out_row = MDBoxLayout(size_hint_y=None, height="48dp", spacing="8dp")
        self.out_input = MDTextField(
            hint_text="Çıkış klasörü",
            mode="rectangle",
            size_hint_y=1,
            md_bg_color=(242/255, 242/255, 242/255, 1),
        )
        out_btn = MDRaisedButton(
            text="Seç",
            size_hint_y=1,
            md_bg_color=(0, 122/255, 254/255, 1),
        )
        out_btn.bind(on_press=lambda *_: app.show_file_picker(pick_dir=True, target_field=self.out_input))
        out_row.add_widget(self.out_input)
        out_row.add_widget(out_btn)

        form.add_widget(self.bind_input)
        form.add_widget(self.port_input)
        form.add_widget(self.chunk_input)
        form.add_widget(out_row)

        scroll.add_widget(form)
        self.add_widget(scroll)

        self.start_btn = MDRaisedButton(
            text="Dinlemeyi Başlat", size_hint_y=None, height="48dp", md_bg_color=(0, 122/255, 254/255, 1)
        )
        self.start_btn.bind(on_press=lambda *_: app.start_action("receive"))
        self.add_widget(self.start_btn)


class P2PApp(MDApp):
    def build(self):
        self.mode = "send"
        self._running = {"send": False, "receive": False}

        root = MDBoxLayout(orientation="vertical", padding="12dp", spacing="8dp", size_hint=(1, 1))

        root.add_widget(
            MDLabel(
                text="P2P Paylaş - PIN Korumalı",
                font_style="H5",
                halign="left",
                theme_text_color="Primary",
                size_hint_y=None,
                height="40dp",
            )
        )

        pin_row = MDBoxLayout(spacing="8dp", size_hint_y=None, height="56dp")
        pin_row.add_widget(
            MDLabel(
                text="PIN",
                size_hint_x=0.25,
                theme_text_color="Secondary",
                halign="left",
            )
        )
        self.pin_input = MDTextField(
            hint_text="PIN (6 rakam)",
            text="123456",
            mode="rectangle",
            size_hint_y=None,
            height="48dp",
            input_filter="int",
            max_text_length=6,
        )
        pin_row.add_widget(self.pin_input)
        root.add_widget(pin_row)

        self.scope_status = MDLabel(
            text="Ağ kapsamı otomatik belirlenecek.",
            font_style="Caption",
            theme_text_color="Secondary",
        )
        root.add_widget(self.scope_status)

        # ===== INPUT FIELDS =====
        self.tabs = MDTabs()
        self.send_tab = SendTab(app=self)
        self.receive_tab = ReceiveTab(app=self)
        self.tabs.add_widget(self.send_tab)
        self.tabs.add_widget(self.receive_tab)
        self.tabs.bind(on_tab_switch=self.on_tab_switch)
        root.add_widget(self.tabs)

        # ===== LOG AREA =====
        log_scroll = MDScrollView(size_hint=(1, None), height="180dp")
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
        
        return root
    
    def _update_log_height(self, *args):
        self.log_label.height = max(self.log_label.texture_size[1], 150)
        self.log_label.text_size = (self.log_label.width, None)
    
    def on_tab_switch(self, _tabs, _tab, tab_label, tab_text):
        # MDTabs passes tab_label widget; tab_text is the displayed title.
        self.mode = "send" if tab_text == "Gönder" else "receive"

    def append_log(self, text: str) -> None:
        if not self.log_label.text.startswith("İşlem kayıtları"):
            self.log_label.text += f"\n{text}"
        else:
            self.log_label.text = text

    def show_file_picker(self, pick_dir: bool, target_field: MDTextField) -> None:
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
                target_field.text = selected
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
        
        popup = Popup(title="Dosya Seç" if not pick_dir else "Klasör Seç", content=content, size_hint=(0.95, 0.95))
        popup.open()

    def _determine_scope(self, addr: str) -> tuple[bool, str]:
        """Return (local_only, reason) based on IP class."""
        if not addr:
            return True, "Adres belirtilmedi; yerel arayüze öncelik verildi."

        try:
            ip_obj = ipaddress.ip_address(addr if addr != "0.0.0.0" else "127.0.0.1")
        except ValueError:
            try:
                resolved = p2p.resolve_ip(addr)
                ip_obj = resolved
            except Exception:
                return False, "Adres çözümlenemedi; WAN kabuluyle devam ediliyor."

        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_unspecified:
            return True, "Yerel IP tespit edildi; LAN önceliklendirildi."
        return False, "Genel IP tespit edildi; WAN bağlantısı kabul edildi."

    def start_action(self, mode: str):
        if self._running.get(mode):
            return

        pin = self.pin_input.text.strip()
        if not pin:
            self.append_log("[!] PIN boş olamaz.")
            return

        tab = self.send_tab if mode == "send" else self.receive_tab

        try:
            port = self._safe_int(tab.port_input.text, 5000, 1, 65535)
            chunk_size = self._safe_int(tab.chunk_input.text, 1024 * 1024, 1)
        except ValueError as e:
            self.append_log(f"[!] Hata: {e}")
            return

        if mode == "send":
            host = tab.host_input.text.strip()
            file_path = Path(tab.file_input.text)
            if not host:
                self.append_log("[!] Alıcı host gerekli.")
                return
            if not file_path.exists():
                self.append_log("[!] Gönderilecek dosya/klasör bulunamadı.")
                return
            local_only, reason = self._determine_scope(host)
            if local_only:
                try:
                    ensure_local(host)
                except Exception as exc:
                    self.append_log(f"[!] {exc}")
                    return
            target_fn = lambda: send_file(host, port, pin, file_path, chunk_size)
        else:
            bind_addr = tab.bind_input.text.strip() or "0.0.0.0"
            output_dir = Path(tab.out_input.text or ".")
            output_dir.mkdir(parents=True, exist_ok=True)
            local_only, reason = self._determine_scope(bind_addr)
            if local_only:
                try:
                    ensure_local(bind_addr)
                except Exception as exc:
                    self.append_log(f"[!] {exc}")
                    return
            target_fn = lambda: receive_file(bind_addr, port, pin, output_dir, chunk_size)

        scope_text = "LAN" if local_only else "WAN"
        self.scope_status.text = f"Ağ kapsamı: {scope_text} (otomatik). {reason}"
        self._run_thread(target_fn, mode, tab.start_btn)

    def _safe_int(self, text: str, default: int, min_val: int, max_val: Optional[int] = None) -> int:
        value = default if not text.strip() else int(text)
        if value < min_val or (max_val and value > max_val):
            raise ValueError("Port ve blok boyutu geçersiz")
        return value

    def _run_thread(self, target_fn, mode: str, start_btn: MDRaisedButton):
        self._running[mode] = True
        start_btn.disabled = True
        writer = LogWriter(lambda t: Clock.schedule_once(lambda *_: self.append_log(t)))

        def runner():
            try:
                with redirect_stdout(writer):
                    target_fn()
                Clock.schedule_once(lambda *_: self.append_log("[✓] Tamamlandı."))
            except Exception as exc:
                Clock.schedule_once(lambda *_: self.append_log(f"[!] Hata: {exc}"))
            finally:
                self._running[mode] = False
                Clock.schedule_once(lambda *_: setattr(start_btn, "disabled", False))

        threading.Thread(target=runner, daemon=True).start()


def launch():
    P2PApp().run()


if __name__ == "__main__":
    launch()
