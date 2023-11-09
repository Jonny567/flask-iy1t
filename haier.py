import requests
import time

class HaierTVRemote:
    def __init__(self, tv_ip, tv_port=56790):
        self.tv_ip = tv_ip
        self.tv_port = tv_port

    def open_connection(self):
        # Open connection to the TV
        url = f"http://{self.tv_ip}:{self.tv_port}/dd.xml"
        headers = {
            "Connection": "Keep-alive",
            "Host": f"{self.tv_ip}:{self.tv_port}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print("Connection to TV opened successfully")
            return True
        else:
            print("Failed to open connection to TV")
            return False

    def send_command(self, command_code):
        if not self.open_connection():
            return

        # Send command to the TV
        url = f"http://{self.tv_ip}:{self.tv_port}/apps/SmartCenter"
        headers = {
            "Content-Type": "text/plain"
        }
        body = f"<?xml version='1.0' ?><remote><key code='{command_code}'/><?xml version='1.0' ?>"

        response = requests.post(url, headers=headers, data=body)

        if response.status_code == 200:
            print(f"Command {command_code} sent successfully")
        else:
            print(f"Failed to send command {command_code}")
