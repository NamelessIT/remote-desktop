import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
import numpy as np
import pyautogui
from aiortc import VideoStreamTrack, RTCPeerConnection, RTCSessionDescription
import asyncio
import av
from common import signaling
# ...



class ScreenTrack(VideoStreamTrack):
    async def recv(self):
        frame = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        av_frame = av.VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts = None
        await asyncio.sleep(1/30)  # 30 FPS
        return av_frame

async def run_server():
    pc = RTCPeerConnection()
    pc.addTrack(ScreenTrack())

    offer_sdp = await signaling.receive()
    offer = RTCSessionDescription(sdp=offer_sdp, type="offer")
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    await signaling.send(pc.localDescription)

    print("Server is running...")
    while True:
        input_data = receive_input()
        if input_data:
            handle_remote_input(input_data)
        await asyncio.sleep(0.01)

    
def handle_remote_input(input_data):
    if input_data == "w":
        pyautogui.press('w')
    elif input_data == "left_click":
        pyautogui.click()

def receive_input():
    try:
        with open(signaling.input_file, "r") as f:
            data = f.read()
        with open(signaling.input_file, "w") as f:
            f.write("")
        return data
    except:
        return ""




if __name__ == "__main__":
    asyncio.run(run_server())

