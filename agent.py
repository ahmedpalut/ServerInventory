import socket
import getpass
import platform
import requests


FLASK_URL = "http://127.0.0.1:5000/api/client/update"


def get_local_ip():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "Unknown"


def send_client_info():
    data = {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "os_name": f"{platform.system()} {platform.release()}",
        "ip_address": get_local_ip()
    }

    try:
        response = requests.post(
            FLASK_URL,
            json=data,
            timeout=5
        )

        print("Flask:", response.status_code)
        print(response.text)

    except requests.RequestException as e:
        print("Flask bağlantı hatası:", e)


if __name__ == "__main__":
    send_client_info()