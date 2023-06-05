import subprocess
import socket


def is_chrome_running_on_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect(('localhost', port))
            return True
        except ConnectionRefusedError:
            return False


if is_chrome_running_on_port(9222):
    print("Chrome is running on port 9222")
else:
    subprocess.Popen(['google-chrome', '--remote-debugging-port=9222'])
    print("Chrome is set for running on port 9222")
