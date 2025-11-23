"""
Basit tkinter arayüzü: sunucusuz P2P dosya gönder/al (PIN doğrulamalı).
Komut satırı yerine form doldurarak çalıştırmak için.
"""
"""
Basit tkinter arayüzü: sunucusuz P2P dosya gönder/al (PIN doğrulamalı).
Komut satırı yerine form doldurarak çalıştırmak için.
"""
from __future__ import annotations

import threading
from contextlib import redirect_stdout
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, StringVar, IntVar
import tkinter as tk

from p2p import send_file, receive_file, ensure_local


class LogWriter:
    """stdout'u arayüz loguna yönlendirmek için hafif yardımcı."""

    def __init__(self, log_fn):
        self.log_fn = log_fn

    def write(self, data: str) -> None:
        text = data.rstrip("\n")
        if text:
            self.log_fn(text)

    def flush(self) -> None:  # stdout uyumluluğu
        return


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("P2P Dosya Aktarımı (PIN korumalı)")
        self.configure(bg="#0f172a")
        self.geometry("760x560")

        self.mode = StringVar(value="send")
        self.host = StringVar(value="127.0.0.1")
        self.bind_addr = StringVar(value="0.0.0.0")
        self.port = IntVar(value=5000)
        self.pin = StringVar(value="123456")
        self.file_path = StringVar()
        self.output_dir = StringVar(value=str(Path.cwd()))
        self.chunk_size = IntVar(value=1024 * 1024)
        self.local_only = IntVar(value=1)  # 1: LAN, 0: Genel

        self._running = False
        self._build_ui()

    def _build_ui(self) -> None:
        header = tk.Label(
            self,
            text="Sunucusuz, PIN korumalı P2P aktarım",
            bg="#0f172a",
            fg="#e2e8f0",
            font=("Segoe UI Semibold", 16),
        )
        header.pack(pady=(18, 8))

        mode_frame = tk.Frame(self, bg="#0f172a")
        mode_frame.pack(pady=4)
        for value, label in (("send", "Gönder"), ("receive", "Al")):
            tk.Radiobutton(
                mode_frame,
                text=label,
                value=value,
                variable=self.mode,
                font=("Segoe UI", 10),
                bg="#0f172a",
                fg="#e2e8f0",
                selectcolor="#1e293b",
                activebackground="#1e293b",
                command=self._toggle_mode,
            ).pack(side=tk.LEFT, padx=6)

        form = tk.Frame(self, bg="#0f172a")
        form.pack(fill=tk.X, padx=20, pady=6)

        self._add_labeled_entry(form, "Pin", self.pin, row=0)
        self._add_labeled_entry(form, "Port", self.port, row=1)
        self._add_labeled_entry(form, "Blok boyutu (bayt)", self.chunk_size, row=2)

        # Send specific
        self.host_row = self._add_labeled_entry(form, "Alıcı host (send)", self.host, row=3)
        self.file_row = self._add_path_picker(form, "Gönderilecek dosya", self.file_path, row=4, pick_file=True)

        # Receive specific
        self.bind_row = self._add_labeled_entry(form, "Dinlenecek adres (receive)", self.bind_addr, row=5)
        self.out_row = self._add_path_picker(form, "Çıkış klasörü", self.output_dir, row=6, pick_file=False)

        net_row = tk.Frame(self, bg="#0f172a")
        net_row.pack(fill=tk.X, padx=20, pady=(4, 2))
        tk.Label(net_row, text="Ağ modu", bg="#0f172a", fg="#cbd5e1", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        tk.Radiobutton(
            net_row,
            text="Yerel ağ (LAN)",
            variable=self.local_only,
            value=1,
            bg="#0f172a",
            fg="#e2e8f0",
            selectcolor="#1e293b",
            activebackground="#1e293b",
        ).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(
            net_row,
            text="Genel (WAN)",
            variable=self.local_only,
            value=0,
            bg="#0f172a",
            fg="#e2e8f0",
            selectcolor="#1e293b",
            activebackground="#1e293b",
        ).pack(side=tk.LEFT, padx=10)

        self.start_btn = tk.Button(
            self,
            text="Başlat",
            bg="#22c55e",
            fg="#0f172a",
            font=("Segoe UI Semibold", 11),
            relief=tk.FLAT,
            padx=12,
            pady=8,
            command=self._start_action,
            activebackground="#16a34a",
            activeforeground="#0f172a",
        )
        self.start_btn.pack(pady=(12, 8))

        self.log_box = scrolledtext.ScrolledText(
            self,
            height=14,
            bg="#0b1220",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            font=("Cascadia Mono", 10),
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#1e293b",
        )
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=14, pady=(4, 12))
        self.log_box.configure(state=tk.DISABLED)

        self._toggle_mode()

    def _add_labeled_entry(self, parent, label: str, variable, row: int, placeholder: str | None = None):
        lbl = tk.Label(parent, text=label, bg="#0f172a", fg="#cbd5e1", font=("Segoe UI", 10))
        lbl.grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)

        entry = tk.Entry(parent, textvariable=variable, width=32, font=("Segoe UI", 10), bg="#1e293b", fg="#e2e8f0", insertbackground="#e2e8f0", relief=tk.FLAT)
        entry.grid(row=row, column=1, sticky="we", pady=4)
        parent.grid_columnconfigure(1, weight=1)
        if placeholder:
            entry.insert(0, placeholder)
        return entry

    def _add_path_picker(self, parent, label: str, variable, row: int, pick_file: bool):
        lbl = tk.Label(parent, text=label, bg="#0f172a", fg="#cbd5e1", font=("Segoe UI", 10))
        lbl.grid(row=row, column=0, sticky="w", padx=(0, 12), pady=4)

        entry = tk.Entry(parent, textvariable=variable, width=32, font=("Segoe UI", 10), bg="#1e293b", fg="#e2e8f0", insertbackground="#e2e8f0", relief=tk.FLAT)
        entry.grid(row=row, column=1, sticky="we", pady=4)
        parent.grid_columnconfigure(1, weight=1)

        def pick():
            if pick_file:
                path = filedialog.askopenfilename(title="Gönderilecek dosyayı seçin")
            else:
                path = filedialog.askdirectory(title="Çıkış klasörü seçin")
            if path:
                variable.set(path)

        btn = tk.Button(parent, text="Seç", command=pick, bg="#334155", fg="#e2e8f0", relief=tk.FLAT, padx=8, pady=4)
        btn.grid(row=row, column=2, padx=(8, 0), pady=4)
        return (entry, btn)

    def _toggle_mode(self):
        mode = self.mode.get()
        send_visible = mode == "send"
        for widget in self.host_row if isinstance(self.host_row, tuple) else (self.host_row,):
            widget_state = tk.NORMAL if send_visible else tk.DISABLED
            try:
                widget.configure(state=widget_state)
            except tk.TclError:
                pass
        for widget in self.file_row if isinstance(self.file_row, tuple) else (self.file_row,):
            try:
                widget.configure(state=tk.NORMAL if send_visible else tk.DISABLED)
            except tk.TclError:
                pass

        recv_visible = mode == "receive"
        for widget in self.bind_row if isinstance(self.bind_row, tuple) else (self.bind_row,):
            try:
                widget.configure(state=tk.NORMAL if recv_visible else tk.DISABLED)
            except tk.TclError:
                pass
        for widget in self.out_row if isinstance(self.out_row, tuple) else (self.out_row,):
            try:
                widget.configure(state=tk.NORMAL if recv_visible else tk.DISABLED)
            except tk.TclError:
                pass

    def log(self, text: str) -> None:
        self.log_box.configure(state=tk.NORMAL)
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)
        self.log_box.configure(state=tk.DISABLED)
        self.update_idletasks()

    def _start_action(self) -> None:
        if self._running:
            return
        try:
            port = int(self.port.get())
            if port <= 0 or port > 65535:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Port 1-65535 arasında olmalı.")
            return
        try:
            chunk_size = int(self.chunk_size.get())
            if chunk_size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Hata", "Blok boyutu pozitif olmalı.")
            return

        mode = self.mode.get()
        pin = self.pin.get().strip()
        if not pin:
            messagebox.showerror("Hata", "PIN boş olamaz.")
            return
        local_only = bool(self.local_only.get())

        if mode == "send":
            host = self.host.get().strip()
            file_path = Path(self.file_path.get())
            if not host:
                messagebox.showerror("Hata", "Alıcı host gerekli.")
                return
            if not file_path.is_file():
                messagebox.showerror("Hata", "Gönderilecek dosya bulunamadı.")
                return
            if local_only:
                try:
                    ensure_local(host)
                except Exception as exc:  # pylint: disable=broad-except
                    messagebox.showerror("Hata", str(exc))
                    return
            target_fn = lambda: send_file(host, port, pin, file_path, chunk_size)
        else:
            bind_addr = self.bind_addr.get().strip() or "0.0.0.0"
            output_dir = Path(self.output_dir.get() or ".")
            if local_only:
                try:
                    ensure_local(bind_addr)
                except Exception as exc:  # pylint: disable=broad-except
                    messagebox.showerror("Hata", str(exc))
                    return
            target_fn = lambda: receive_file(bind_addr, port, pin, output_dir, chunk_size)

        self._run_thread(target_fn)

    def _run_thread(self, target_fn) -> None:
        self._running = True
        self.start_btn.configure(state=tk.DISABLED, text="Çalışıyor...")
        writer = LogWriter(self.log)

        def runner():
            try:
                with redirect_stdout(writer):
                    target_fn()
                self.log("[✓] İşlem tamamlandı.")
            except Exception as exc:  # pylint: disable=broad-except
                self.log(f"[!] Hata: {exc}")
                messagebox.showerror("Hata", str(exc))
            finally:
                self._running = False
                self.start_btn.configure(state=tk.NORMAL, text="Başlat")

        threading.Thread(target=runner, daemon=True).start()


def launch() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    launch()
