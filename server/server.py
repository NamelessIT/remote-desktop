# server.py
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

class ScreenTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.width, self.height = pyautogui.size()

    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        av_frame = av.VideoFrame.from_ndarray(frame, format="bgr24")
        av_frame.pts = pts
        av_frame.time_base = time_base

        await asyncio.sleep(1/30)  # 30 FPS
        return av_frame

async def run_server():
    pc = RTCPeerConnection()

    @pc.on("datachannel")
    def on_datachannel(channel):
        print(f"[SERVER] DataChannel {channel.label} received")

        @channel.on("message")
        def on_message(message):
            handle_remote_input(message)

    offer_sdp = await signaling.receive()

    # Fix SDP nếu thiếu a=sendrecv
    sdp_lines = offer_sdp.splitlines()
    has_video = any(line.startswith("m=video") for line in sdp_lines)
    new_sdp_lines = []
    in_application = False

    for line in sdp_lines:
        new_sdp_lines.append(line)
        if line.startswith("m=application"):
            in_application = True
        elif in_application and line.startswith("a="):
            if "sendrecv" not in line and not any(d in line for d in ["sendonly", "recvonly", "inactive"]):
                new_sdp_lines.append("a=sendrecv")
                in_application = False
        elif in_application and line.strip() == "":
            new_sdp_lines.append("a=sendrecv")
            in_application = False

    if in_application:
        new_sdp_lines.append("a=sendrecv")

    fixed_offer_sdp = "\n".join(new_sdp_lines)

    offer = RTCSessionDescription(sdp=fixed_offer_sdp, type="offer")
    await pc.setRemoteDescription(offer)

    if has_video:
        pc.addTrack(ScreenTrack())

    answer = await pc.createAnswer()

    # In ra kiểm tra
    print("Original answer SDP:\n", answer.sdp)

    # Replace actpass -> passive
    sdp = answer.sdp.replace("a=setup:actpass", "a=setup:passive")
    modified_answer = RTCSessionDescription(sdp=sdp, type=answer.type)

    await pc.setLocalDescription(modified_answer)
    await signaling.send(modified_answer.sdp)



    await asyncio.Future()  # giữ server chạy

def handle_remote_input(input_data):
    if input_data == "w":
        pyautogui.press('w')
    elif input_data == "left_click":
        pyautogui.click()

if __name__ == "__main__":
    asyncio.run(run_server())
