import requests
import json
import platform
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from requests.models import Response

#global variables
CONFIG: str = "report_stats_config.txt"
WINDOWS: str = "Windows"
LINUX: str = "Linux"

#config variables
postUrl: str = ""
operatingSystem: str = ""
battletimeModuleName: str = ""
statsJsonName: str = ""
wseFolderWindows: str = ""
wseFolderLinux: str = ""
payloadLocation: str = ""

def initalize() -> bool:
    global operatingSystem
    global payloadLocation

    operatingSystem  = platform.system()
    settings = open(CONFIG, "r")

    for line in settings:
        line = line.strip()
        
        if line == "" or line[0] == "#":
            continue
        setting: list[str] = line.split("=")

        settingType: str = setting.pop(0)
        settingValue: str = ''.join(setting)
        globals()[settingType] = settingValue

    if postUrl == "":
        print(f"postUrl undefined! Check {CONFIG}") 
        return False
    print("POST url set")

    if wseFolderWindows == "" and operatingSystem == WINDOWS:
        print(f"wseFolderWindows undefined! Check {CONFIG}")
        return False
    if wseFolderLinux == "" and operatingSystem == LINUX:
        print(f"wseFolderLinux undefined! Check {CONFIG}")
        return False
        
    if operatingSystem == WINDOWS:
        payloadLocation = wseFolderWindows
    elif operatingSystem == LINUX:
        payloadLocation = wseFolderLinux
    else:
        print("Operating system undefined! Mac user??")
        return False

    if payloadLocation[0] == "~":
        payloadLocation = payloadLocation.replace("~", getHomeUserFolder())
 
    payloadLocation += f"{battletimeModuleName}/{statsJsonName}"

    print(f"Payload location set")
    return True

def getHomeUserFolder() -> str:
    if operatingSystem == WINDOWS:
        return os.path.expanduser("~")
    elif operatingSystem == LINUX:    
        user = os.environ.get("SUDO_USER", os.environ.get("USERNAME"))
        home = f"/home/{user}" 
        return home
    return ""


def getPayload() -> str:
    try: 
        payloadFile = open(payloadLocation, "r")
        payload: str = json.load(payloadFile)
        #payload["Time"] = datetime.now().strftime("%x, %X")
    except Exception as e:
        payload = ""
    
    return payload

def archivePayload():
    os.rename(payloadLocation, payloadLocation+".archive")       

def post() -> str:
    payload:str = getPayload()
    if payload == "":
        print("No payload found!")
        print(f"Is this the right filepath? {payloadLocation}")
        return ""

    headers: dict[str,str] = {'content-type' : 'application/json'}
    response: Response 
    response = requests.post(postUrl, headers=headers, json=payload)
    return response.text


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()       
        _ = self.wfile.write(bytes("Pendor Battletime Stats!", "utf-8"))

    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers() 

            print("Uploading stats")
            stats_post_callback: str
            stats_post_callback = post()
            if stats_post_callback == "":
                stats_post_callback = "Upload failed! Check if payload exists and the POST url is correct"

            print(stats_post_callback)
            #archivePayload();
            _ = self.wfile.write(bytes(stats_post_callback, "utf-8"))

        except Exception as e: 
            print(e)
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            _ = self.wfile.write(bytes("Upload failed! Check if payload exists and the POST url is correct", 'utf-8'))


def main():
    if initalize() is False:
        return
    try:
        port: int
        port = 80 
        print(f"Starting server on localhost:{port}")
        with HTTPServer(('localhost', port), handler) as server:
            server.serve_forever()
    except Exception as e:
        print(e)
        print("Failed to start server. Are you running as administrator?")
    except KeyboardInterrupt:
        print("Closing server")
        server.socket.close()


if __name__ == '__main__':
    main()
