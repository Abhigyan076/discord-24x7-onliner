import colorama
from colorama import Fore
colorama.init(autoreset=True)

ascii_art = [
    " ▄▄▄▄▄▄▄    ▄▄▄▄▄▄▄    ▄▄   ▄▄   ▄▄▄▄▄▄▄ ",
    "▐░░░░░░░▌  ▐░░░░░░░▌  ▐░░▌ ▐░░▌ ▐░░░░░░░▌",
    "▐░█▀▀▀█░▌  ▐░█▀▀▀█░▌  ▐░█▀▀▀█░▌  ▀▀█░█▀▀ ",
    "▐░█▄▄▄█░▌  ▐░█▄▄▄█░▌  ▐░█   █░▌    ▐░▌   ",
    "▐░░░░░░░▌  ▐░█▀▀▀█░▌  ▐░█   █░▌    ▐░▌   ",
    "▐░█▀▀▀█░▌  ▐░█▄▄▄█░▌  ▐░█   █░▌  ▄▄█░█▄▄ ",
    "▐░█   ▐░▌  ▐░░░░░░░▌  ▐░█   █░▌ ▐░░░░░░░▌",
    " ▀     ▀    ▀▀▀▀▀▀▀    ▀     ▀   ▀▀▀▀▀▀▀ "
]

colors = [Fore.RED, Fore.LIGHTRED_EX, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX]

for i, line in enumerate(ascii_art):
    print(colors[i % len(colors)] + line)
import json
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import websocket, asyncio, ssl
from colorama import Fore
#import pyfade

types = ['Playing', 'Streaming', 'Watching', 'Listening']
status = ['online', 'dnd', 'idle']

############################################ Change here

GAME = "MY TEXT2"  # enter what you want the status to be
type_ = types[0]  # 0: Playing, 1: Streaming, 2: Watching, 3: Listening
status = status[0]  # 0: Online, 1: Do Not Disturb, 2: Idle
random_ = True  # True: Random status and type, False: Game status and type
stream_text = "MY TEXT"  # enter what you want the stream to be

############################################ Stop changing here

with open("tokens.txt", "r") as f:
    al = [line.strip() for line in f.read().split("\n") if line.strip()]

if not al:
    print(f"{Fore.RED}[!] No tokens found in tokens.txt")
    exit()
elif len(al) == 1:
    print(f"{Fore.GREEN}[i] 1 token found in tokens.txt")
else:
    print(f"{Fore.GREEN}[i] {len(al)} tokens found in tokens.txt")

print("[i] Starting...")

c = 0
l = len(al)

def online(token, game, type, status_val):
    global c
    global l
    
    retry_delay = 5
    while True:
        ws = websocket.WebSocket()
        try:
            ws.connect('wss://gateway.discord.gg/?v=10&encoding=json')
        except ssl.SSLError:
            try:
                ws.connect('wss://gateway.discord.gg/?v=10&encoding=json', sslopt={"cert_reqs": ssl.CERT_NONE})
            except Exception as e:
                print(f"{Fore.RED}[!] SSL connection error for token {token[:15]}...: {e}")
                time.sleep(retry_delay)
                continue
        except Exception as e:
            print(f"{Fore.RED}[!] Connection error for token {token[:15]}...: {e}")
            time.sleep(retry_delay)
            continue

        try:
            hello = json.loads(ws.recv())
            heartbeat_interval = hello['d']['heartbeat_interval']
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to receive Hello for token {token[:15]}...: {e}")
            ws.close()
            time.sleep(retry_delay)
            continue

        current_type = type
        current_status = status_val
        current_game = game

        if random_:
            current_type = random.choice(['Playing', 'Streaming', 'Watching', 'Listening', ''])
            current_status = random.choice(['online', 'dnd', 'idle'])

        gamejson = None
        if current_type == "Playing":
            if random_:
                current_game = random.choice(["Minecraft", "Badlion", "Roblox", "The Elder Scrolls: Online", "DCS World Steam Edit", ])
            gamejson = {
                "name": current_game,
                "type": 0
            }
        elif current_type == 'Streaming':
            gamejson = {
                "name": current_game,
                "type": 1,
                "url": stream_text
            }
        elif current_type == "Listening":
            if random_:
                current_game = random.choice(["Spotify", "Deezer", "Apple Music", "YouTube", "SoundCloud", "Pandora", "Tidal", "Amazon Music", "Google Play Music", "Apple Podcasts", "iTunes", "Beatport"])
            gamejson = {
                "name": current_game,
                "type": 2
            }
        elif current_type == "Watching":
            if random_:
                current_game = random.choice(["YouTube", "Twitch"])
            gamejson = {
                "name": current_game,
                "type": 3
            }
        else:
            gamejson = {
                "name": current_game,
                "type": 0
            }

        auth = {
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "os": sys.platform,
                    "browser": "chrome",
                    "device": ""
                },
                "presence": {
                    "activities": [gamejson] if gamejson else [],
                    "status": current_status,
                    "since": 0,
                    "afk": False
                }
            }
        }

        try:
            ws.send(json.dumps(auth))
        except Exception as e:
            print(f"{Fore.RED}[!] Failed to send Identify for token {token[:15]}...: {e}")
            ws.close()
            time.sleep(retry_delay)
            continue

        # Wait for READY or CLOSE frame to verify auth
        is_ready = False
        try:
            frame = ws.recv_frame()
            if not frame:
                print(f"{Fore.RED}[!] Connection closed immediately for token {token[:15]}...")
                ws.close()
                time.sleep(retry_delay)
                continue
            if frame.opcode == websocket.ABNF.OPCODE_CLOSE:
                code = int.from_bytes(frame.data[:2], byteorder='big') if len(frame.data) >= 2 else 1000
                reason = frame.data[2:].decode('utf-8', errors='ignore') if len(frame.data) >= 2 else ""
                print(f"{Fore.RED}[!] Token {token[:15]}... failed to authenticate. Code: {code}, Reason: {reason}")
                ws.close()
                if code == 4004:
                    return
                time.sleep(retry_delay)
                continue

            msg = json.loads(frame.data.decode('utf-8') if isinstance(frame.data, bytes) else frame.data)
            if msg.get('t') == 'READY':
                is_ready = True
                c += 1
                print(f"{Fore.GREEN}[i] {token} is online {c}/{l}")
        except Exception as e:
            print(f"{Fore.RED}[!] Error during authentication for token {token[:15]}...: {e}")
            ws.close()
            time.sleep(retry_delay)
            continue

        ack = {
            "op": 1,
            "d": None
        }
        next_heartbeat = time.time() + (heartbeat_interval / 1000) * random.random()
        should_reconnect = False

        while not should_reconnect:
            try:
                now = time.time()
                time_to_heartbeat = next_heartbeat - now
                if time_to_heartbeat <= 0:
                    ws.send(json.dumps(ack))
                    next_heartbeat = time.time() + heartbeat_interval / 1000
                    continue

                ws.settimeout(max(0.1, time_to_heartbeat))
                frame = ws.recv_frame()
                if not frame:
                    print(f"{Fore.RED}[!] Connection closed for token {token[:15]}...")
                    should_reconnect = True
                    break

                if frame.opcode == websocket.ABNF.OPCODE_CLOSE:
                    code = int.from_bytes(frame.data[:2], byteorder='big') if len(frame.data) >= 2 else 1000
                    reason = frame.data[2:].decode('utf-8', errors='ignore') if len(frame.data) >= 2 else ""
                    print(f"{Fore.RED}[!] Connection closed for token {token[:15]}... Code: {code}, Reason: {reason}")
                    if code == 4004:
                        return
                    should_reconnect = True
                    break

                if frame.opcode == websocket.ABNF.OPCODE_TEXT:
                    msg = json.loads(frame.data.decode('utf-8') if isinstance(frame.data, bytes) else frame.data)
                    if msg.get('op') == 7:
                        print(f"{Fore.YELLOW}[i] Token {token[:15]}... received reconnect request (op 7). Reconnecting...")
                        should_reconnect = True
                        break
            except websocket.WebSocketTimeoutException:
                pass
            except websocket.WebSocketConnectionClosedException:
                print(f"{Fore.RED}[!] Connection closed for token {token[:15]}...")
                should_reconnect = True
                break
            except Exception as e:
                print(f"{Fore.RED}[!] Error in loop for token {token[:15]}...: {e}")
                should_reconnect = True
                break

        ws.close()
        if should_reconnect:
            c = max(0, c - 1)
            time.sleep(retry_delay)

threads = []
for i in range(l):
    t = threading.Thread(target=online, args=(al[i], GAME, type_, status)).start()

print(f"{Fore.GREEN} [+] Tokens are online")
