import socket


def get_local_ip() -> str:
    """Obtém o IP local da máquina na rede (LAN), usado para montar a URL do QR Code."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return socket.gethostbyname(socket.gethostname())
    finally:
        s.close()
