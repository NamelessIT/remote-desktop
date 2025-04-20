import asyncio
import os

BASE_DIR = os.path.dirname(__file__)  # thư mục common

signal_file = os.path.join(BASE_DIR, "signal.txt")
input_file = os.path.join(BASE_DIR, "input.txt")

# Tạo file nếu chưa tồn tại
if not os.path.exists(signal_file):
    open(signal_file, "w").close()

if not os.path.exists(input_file):
    open(input_file, "w").close()


async def send(data):
    with open(signal_file, "w") as f:
        if hasattr(data, 'sdp'):
            print(f"[SIGNAL] Sending SDP {data.type}")
            f.write(data.sdp)
        else:
            f.write(data)

async def receive():
    while True:
        with open(signal_file, "r") as f:
            sdp = f.read()
            if sdp:
                print("[SIGNAL] Received SDP:")
                print(sdp)
                return sdp
        await asyncio.sleep(0.1)




def send_input(input_data):
    with open(input_file, "w") as f:
        f.write(input_data)
