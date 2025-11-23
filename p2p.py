#!/usr/bin/env python3
"""
PIN korumalı, sunucusuz P2P dosya aktarımı.
Gönderici ve alıcı aynı betiği kullanır; bir taraf `receive`, diğer taraf `send` çalıştırır.
"""
from __future__ import annotations

import argparse
import hmac
import hashlib
import ipaddress
import secrets
import shutil
import socket
import struct
import sys
import tempfile
import time
from pathlib import Path
from typing import Tuple


MAGIC = b"P2P1"
HANDSHAKE_SALT = b"p2p-pin-salt"
NONCE_SIZE = 16
HASH_SIZE = 32


def get_optimal_chunk_size(file_size: int) -> int:
    """
    Dynamically determine optimal TCP buffer size based on file size.
    
    - < 10 MB: 64 KB (low RAM footprint)
    - 10 MB - 100 MB: 1 MB
    - 100 MB - 1 GB: 4 MB
    - > 1 GB: 8 MB (maximizes Gigabit LAN throughput)
    """
    if file_size < 10 * 1024 * 1024:  # < 10 MB
        return 64 * 1024
    elif file_size < 100 * 1024 * 1024:  # < 100 MB
        return 1024 * 1024
    elif file_size < 1024 * 1024 * 1024:  # < 1 GB
        return 4 * 1024 * 1024
    else:  # >= 1 GB
        return 8 * 1024 * 1024


def derive_key(pin: str) -> bytes:
    """Derive a stable key from the PIN to use for HMAC authentication."""
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), HANDSHAKE_SALT, 100_000, dklen=32)


def recv_exact(conn: socket.socket, num_bytes: int) -> bytes:
    """Receive exactly num_bytes or raise on unexpected EOF."""
    buf = bytearray()
    while len(buf) < num_bytes:
        chunk = conn.recv(num_bytes - len(buf))
        if not chunk:
            raise ConnectionError("Bağlantı beklenmedik şekilde kapandı.")
        buf.extend(chunk)
    return bytes(buf)


def handshake(conn: socket.socket, key: bytes, initiator: bool) -> None:
    """
    HMAC tabanlı karşılıklı doğrulama.
    Server (alıcı) nonce gönderir; client (gönderici) HMAC ile yanıtlar.
    """
    if initiator:
        peer_nonce = recv_exact(conn, NONCE_SIZE)
        token = hmac.new(key, MAGIC + peer_nonce, hashlib.sha256).digest()
        conn.sendall(token)
        status = recv_exact(conn, 2)
        if status != b"OK":
            raise PermissionError("PIN doğrulaması başarısız.")
    else:
        nonce = secrets.token_bytes(NONCE_SIZE)
        conn.sendall(nonce)
        token = recv_exact(conn, HASH_SIZE)
        expected = hmac.new(key, MAGIC + nonce, hashlib.sha256).digest()
        if not hmac.compare_digest(token, expected):
            conn.sendall(b"NO")
            raise PermissionError("PIN doğrulaması başarısız.")
        conn.sendall(b"OK")


def resolve_ip(addr: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
    """
    Resolve host/address to an IP object. Raises if resolution fails.
    Prefers literal parsing; falls back to DNS/hosts.
    """
    try:
        return ipaddress.ip_address(addr)
    except ValueError:
        # Try resolve hostname
        resolved = socket.gethostbyname(addr)
        return ipaddress.ip_address(resolved)


def ensure_local(addr: str) -> None:
    """
    Ensure the given host/bind is private or loopback.
    Raises ValueError if not.
    """
    ip_obj = resolve_ip(addr)
    if not (ip_obj.is_private or ip_obj.is_loopback):
        raise ValueError(f"{addr} yerel degil; yerel IP veya localhost kullanin.")


def send_file(host: str, port: int, pin: str, file_path: Path, chunk_size: int = None) -> None:
    key = derive_key(pin)
    file_path = Path(file_path)
    
    # Auto-determine chunk size if not provided
    if chunk_size is None:
        chunk_size = 1024 * 1024  # Default 1 MB
    
    # Handle directory: automatically zip it
    temp_zip = None
    if file_path.is_dir():
        print(f"[+] Dizin algılandı: {file_path}")
        print(f"[+] Arşivleniyor...")
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_zip = Path(tmpdir) / f"{file_path.name}.zip"
            shutil.make_archive(str(temp_zip.with_suffix('')), 'zip', file_path)
            file_path = temp_zip
            print(f"[+] Arşiv oluşturuldu: {file_path}")
            _send_file_internal(host, port, pin, key, file_path, chunk_size)
    else:
        if not file_path.is_file():
            raise FileNotFoundError(f"Gönderilecek dosya bulunamadı: {file_path}")
        _send_file_internal(host, port, pin, key, file_path, chunk_size)


def _send_file_internal(host: str, port: int, pin: str, key: bytes, file_path: Path, chunk_size: int) -> None:
    """Internal function to send a file with automatic chunk size optimization."""
    size = file_path.stat().st_size
    
    # Auto-optimize chunk size if it looks like default
    if chunk_size == 1024 * 1024:
        optimal_size = get_optimal_chunk_size(size)
        if optimal_size != chunk_size:
            print(f"[+] Blok boyutu optimize edildi: {chunk_size} -> {optimal_size} (dosya boyutu: {size} bayt)")
            chunk_size = optimal_size
    
    name_bytes = file_path.name.encode("utf-8")
    if len(name_bytes) > 65535:
        raise ValueError("Dosya adı çok uzun.")

    print(f"[+] {file_path} ({size} bayt) gönderiliyor -> {host}:{port}")
    start = time.time()

    with socket.create_connection((host, port), timeout=10) as conn:
        conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        handshake(conn, key, initiator=True)

        conn.sendall(struct.pack(">H", len(name_bytes)) + name_bytes + struct.pack(">Q", size))

        sha = hashlib.sha256()
        sent = 0
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha.update(chunk)
                conn.sendall(chunk)
                sent += len(chunk)
                if sent and sent % (50 * chunk_size) == 0:
                    print(f"    gönderildi: {sent}/{size} bayt")

        conn.sendall(sha.digest())
        status = recv_exact(conn, 2)
        duration = time.time() - start
        speed = size / duration / (1024 * 1024) if duration > 0 else 0
        if status != b"OK":
            raise ConnectionError("Alıcı doğrulama hatası bildirdi.")
        print(f"[✓] Aktarım tamamlandı ({duration:.2f}s, {speed:.2f} MiB/s).")


def unique_target(path: Path) -> Path:
    """Avoid overwriting: append numeric suffix if needed."""
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    parent = path.parent
    for i in range(1, 10_000):
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise FileExistsError("Uygun hedef adı bulunamadı (çok fazla çakışma).")


def receive_file(bind: str, port: int, pin: str, output_dir: Path, chunk_size: int = None) -> None:
    key = derive_key(pin)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Auto-determine chunk size if not provided
    if chunk_size is None:
        chunk_size = 1024 * 1024  # Default 1 MB

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((bind, port))
        srv.listen(1)
        print(f"[+] Dinleniyor: {bind}:{port}")
        conn, addr = srv.accept()
        with conn:
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            print(f"[+] Bağlandı: {addr[0]}:{addr[1]}")
            handshake(conn, key, initiator=False)

            name_len = struct.unpack(">H", recv_exact(conn, 2))[0]
            name = recv_exact(conn, name_len).decode("utf-8", errors="replace")
            size = struct.unpack(">Q", recv_exact(conn, 8))[0]
            
            # Auto-optimize chunk size based on incoming file size
            if chunk_size == 1024 * 1024:
                optimal_size = get_optimal_chunk_size(size)
                if optimal_size != chunk_size:
                    print(f"[+] Blok boyutu optimize edildi: {chunk_size} -> {optimal_size} (dosya boyutu: {size} bayt)")
                    chunk_size = optimal_size

            target = unique_target(output_dir / name)
            print(f"[+] Alınıyor -> {target} (beklenen {size} bayt)")

            sha = hashlib.sha256()
            remaining = size
            start = time.time()
            with target.open("wb") as f:
                while remaining > 0:
                    chunk = conn.recv(min(chunk_size, remaining))
                    if not chunk:
                        raise ConnectionError("Beklenmedik bağlantı kesildi.")
                    f.write(chunk)
                    sha.update(chunk)
                    remaining -= len(chunk)
            expected_hash = recv_exact(conn, HASH_SIZE)
            actual_hash = sha.digest()
            ok = hmac.compare_digest(actual_hash, expected_hash)
            if ok:
                conn.sendall(b"OK")
                duration = time.time() - start
                speed = size / duration / (1024 * 1024) if duration > 0 else 0
                print(f"[✓] Aktarım başarıyla doğrulandı ({duration:.2f}s, {speed:.2f} MiB/s).")
            else:
                conn.sendall(b"NO")
                try:
                    target.unlink()
                except FileNotFoundError:
                    pass
                raise ValueError("Hash eşleşmedi; dosya silindi.")


def positive_int(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("Değer pozitif olmalı.")
    return ivalue


def parse_args(argv: Tuple[str, ...]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PIN korumalı, sunucusuz P2P dosya gönderme/alma aracı."
    )
    parser.add_argument("--chunk-size", type=positive_int, default=1024 * 1024, help="Blok boyutu (bayt). Varsayılan 1 MiB.")

    subparsers = parser.add_subparsers(dest="command", required=True)

    recv_p = subparsers.add_parser("receive", help="Dosya kabul et (dinleyici).")
    recv_p.add_argument("--bind", default="0.0.0.0", help="Dinleme adresi (varsayılan 0.0.0.0).")
    recv_p.add_argument("--port", type=int, required=True, help="Dinlenecek port.")
    recv_p.add_argument("--pin", required=True, help="Paylaşılan PIN.")
    recv_p.add_argument("--output-dir", type=Path, default=Path("."), help="Dosyanın yazılacağı klasör.")
    recv_p.add_argument("--local-only", action="store_true", help="Sadece yerel ağdan erişime izin ver (bind adresi özel/loopback olmalı).")

    send_p = subparsers.add_parser("send", help="Dosya gönder.")
    send_p.add_argument("--host", required=True, help="Alıcı adresi.")
    send_p.add_argument("--port", type=int, required=True, help="Alıcı portu.")
    send_p.add_argument("--pin", required=True, help="Paylaşılan PIN.")
    send_p.add_argument("--file", type=Path, required=True, help="Gönderilecek dosya yolu.")
    send_p.add_argument("--local-only", action="store_true", help="Hedef adres yerel/özel IP olmalı.")

    return parser.parse_args(argv)


def main(argv: Tuple[str, ...]) -> int:
    args = parse_args(argv)
    try:
        if args.command == "send":
            if args.local_only:
                ensure_local(args.host)
            send_file(args.host, args.port, args.pin, args.file, args.chunk_size)
        elif args.command == "receive":
            if args.local_only:
                ensure_local(args.bind)
            receive_file(args.bind, args.port, args.pin, args.output_dir, args.chunk_size)
        else:
            raise ValueError("Geçersiz komut.")
    except KeyboardInterrupt:
        print("\n[!] Kullanıcı tarafından iptal edildi.")
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"[!] Hata: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(tuple(sys.argv[1:])))
