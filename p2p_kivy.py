"""
Kivy tabanlı (Android uyumlu) P2P dosya gönder/al arayüzü.
Gönderici ve alıcı arasında sunucusuz, PIN doğrulamalı aktarım için p2p.py üzerindeki fonksiyonları kullanır.

Android APK üretimi için buildozer/python-for-android ile paketlenebilir.
"""
from __future__ import annotations

import threading
from contextlib import redirect_stdout
from pathlib import Path
from typing import Callable

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView

from p2p import send_file, receive_file, ensure_local


class LogWriter:
    """stdout'u Kivy log ekranına yönlendirmek için."""

    def __init__(self, append_fn: Callable[[str], None]):
        self.append_fn = append_fn

    def write(self, data: str) -> None:
        text = data.rstrip("\n")
        if text:
            self.append_fn(text)

    def flush(self) -> None:
        return


class PickerPopup(Popup):
    """Dosya/klasör seçici."""

    def __init__(self, target_input: TextInput, select_dir: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.target_input = target_input
        self.select_dir = select_dir
        self.title = "Klasör seç" if select_dir else "Dosya seç"
        self.size_hint = (0.9, 0.9)

        chooser = FileChooserListView(
            path=str(Path.home()),
            dirselect=select_dir,
            filters=None,
        )
        chooser.bind(on_submit=self._on_submit)
        self.content = chooser

    def _on_submit(self, chooser, selection, touch):
        if selection:
            self.target_input.text = selection[0]
            self.dismiss()


class P2PApp(App):
    def build(self):
        self.mode = "send"
        root = BoxLayout(orientation="vertical", padding=12, spacing=10)

        header = Label(
            text="Sunucusuz P2P (PIN korumalı)",
            font_size="18sp",
            size_hint=(1, None),
            height=32,
        )
        root.add_widget(header)

        # Mode switch
        mode_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=40, spacing=8)
        mode_row.add_widget(Label(text="Gönder / Al", size_hint=(0.4, 1)))
        self.mode_switch = Switch(active=True)
        self.mode_switch.bind(active=self.on_mode_toggle)
        mode_row.add_widget(self.mode_switch)
        root.add_widget(mode_row)

        scope_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=40, spacing=8)
        scope_row.add_widget(Label(text="Yerel ağ", size_hint=(0.4, 1)))
        self.scope_switch = Switch(active=True)  # True: LAN, False: WAN
        scope_row.add_widget(self.scope_switch)
        scope_row.add_widget(Label(text="Genel", size_hint=(0.2, 1)))
        root.add_widget(scope_row)

        self.pin_input = self._add_field(root, "PIN", "123456")
        self.port_input = self._add_field(root, "Port", "5000", input_filter="int")
        self.chunk_input = self._add_field(root, "Blok boyutu (bayt)", "1048576", input_filter="int")

        self.host_input = self._add_field(root, "Alıcı host (send)", "192.168.1.50")
        self.file_input = self._add_field_with_picker(root, "Gönderilecek dosya", pick_dir=False)

        self.bind_input = self._add_field(root, "Dinlenecek adres (receive)", "0.0.0.0")
        self.out_input = self._add_field_with_picker(root, "Çıkış klasörü", pick_dir=True)

        btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=46, spacing=8)
        self.start_btn = Button(text="Başlat", size_hint=(1, 1), background_color=(0.13, 0.8, 0.45, 1))
        self.start_btn.bind(on_press=lambda _: self.start_action())
        btn_row.add_widget(self.start_btn)
        root.add_widget(btn_row)

        self.log_label = Label(text="", halign="left", valign="top", size_hint_y=None, markup=True)
        self.log_label.bind(texture_size=self._update_log_height)
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.log_label)
        root.add_widget(scroll)

        self._toggle_visibility()
        return root

    def _add_field(self, root, title: str, default: str = "", input_filter=None) -> TextInput:
        row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=46, spacing=8)
        row.add_widget(Label(text=title, size_hint=(0.45, 1)))
        ti = TextInput(text=default, multiline=False, size_hint=(0.55, 1), input_filter=input_filter)
        row.add_widget(ti)
        root.add_widget(row)
        return ti

    def _add_field_with_picker(self, root, title: str, pick_dir: bool) -> TextInput:
        row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=46, spacing=8)
        row.add_widget(Label(text=title, size_hint=(0.35, 1)))
        ti = TextInput(text="", multiline=False, size_hint=(0.5, 1))
        pick_btn = Button(text="Seç", size_hint=(0.15, 1))
        pick_btn.bind(on_press=lambda _: PickerPopup(ti, select_dir=pick_dir).open())
        row.add_widget(ti)
        row.add_widget(pick_btn)
        root.add_widget(row)
        return ti

    def _update_log_height(self, *_):
        self.log_label.height = max(self.log_label.texture_size[1], self.log_label.parent.height)
        self.log_label.text_size = (self.log_label.width, None)

    def on_mode_toggle(self, _instance, value: bool):
        self.mode = "send" if value else "receive"
        self._toggle_visibility()

    def _toggle_visibility(self):
        send_mode = self.mode == "send"
        # host & file visible in send mode
        self.host_input.parent.height = 46 if send_mode else 0
        self.host_input.parent.opacity = 1 if send_mode else 0
        self.file_input.parent.height = 46 if send_mode else 0
        self.file_input.parent.opacity = 1 if send_mode else 0
        # bind & out visible in receive mode
        recv_mode = not send_mode
        self.bind_input.parent.height = 46 if recv_mode else 0
        self.bind_input.parent.opacity = 1 if recv_mode else 0
        self.out_input.parent.height = 46 if recv_mode else 0
        self.out_input.parent.opacity = 1 if recv_mode else 0

    def append_log(self, text: str) -> None:
        self.log_label.text += f"{text}\n"
        self.log_label.texture_update()
        Clock.schedule_once(lambda *_: self._update_log_height())

    def start_action(self):
        if getattr(self, "_running", False):
            return
        try:
            port = int(self.port_input.text)
            chunk_size = int(self.chunk_input.text)
            if port <= 0 or port > 65535 or chunk_size <= 0:
                raise ValueError
        except ValueError:
            self.append_log("[!] Port 1-65535 ve blok boyutu pozitif olmalı.")
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
            if not file_path.is_file():
                self.append_log("[!] Gönderilecek dosya bulunamadı.")
                return
            if local_only:
                try:
                    ensure_local(host)
                except Exception as exc:  # pylint: disable=broad-except
                    self.append_log(f"[!] {exc}")
                    return
            target_fn = lambda: send_file(host, port, pin, file_path, chunk_size)
        else:
            bind_addr = self.bind_input.text.strip() or "0.0.0.0"
            output_dir = Path(self.out_input.text or ".")
            if local_only:
                try:
                    ensure_local(bind_addr)
                except Exception as exc:  # pylint: disable=broad-except
                    self.append_log(f"[!] {exc}")
                    return
            target_fn = lambda: receive_file(bind_addr, port, pin, output_dir, chunk_size)

        self._run_thread(target_fn)

    def _run_thread(self, target_fn):
        self._running = True
        self.start_btn.disabled = True
        writer = LogWriter(lambda t: Clock.schedule_once(lambda *_: self.append_log(t)))

        def runner():
            try:
                with redirect_stdout(writer):
                    target_fn()
                Clock.schedule_once(lambda *_: self.append_log("[✓] Tamamlandı."))
            except Exception as exc:  # pylint: disable=broad-except
                Clock.schedule_once(lambda *_: self.append_log(f"[!] Hata: {exc}"))
            finally:
                self._running = False
                Clock.schedule_once(lambda *_: setattr(self.start_btn, "disabled", False))

        threading.Thread(target=runner, daemon=True).start()


def launch():
    P2PApp().run()


if __name__ == "__main__":
    launch()
