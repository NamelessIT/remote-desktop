# client.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
from aiortc import RTCPeerConnection
import asyncio
import pyautogui
from aiortc import RTCSessionDescription
from common import signaling
import keyboard
import mouse

async def run_client():
    pc = RTCPeerConnection()
    channel = pc.createDataChannel("chat")

    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await signaling.send(pc.localDescription)

    answer_sdp = await signaling.receive()
    print("[SIGNAL] Received Answer SDP:\n", answer_sdp)

    answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
    await pc.setRemoteDescription(answer)

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            async def recv_video():
                while True:
                    frame = await track.recv()
                    img = frame.to_ndarray(format="bgr24")
                    cv2.imshow("Remote Screen", img)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                cv2.destroyAllWindows()
            asyncio.create_task(recv_video())

    await handle_input(channel)

async def handle_input(channel):
    while True:
        if keyboard.is_pressed("w"):
            channel.send("w")
        if mouse.is_pressed(button='left'):
            channel.send("left_click")
        await asyncio.sleep(0.01)

async def main():
    await run_client()

asyncio.run(main())
