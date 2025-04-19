import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import cv2
from aiortc import RTCPeerConnection
import asyncio
import pyautogui
from aiortc.contrib.media import MediaPlayer
from aiortc import RTCSessionDescription
from common import signaling
import keyboard
import mouse

async def run_client():
    pc = RTCPeerConnection()

    pc.createDataChannel("chat")
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await signaling.send(pc.localDescription)

    answer_sdp = await signaling.receive()
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

    await asyncio.sleep(99999)


async def handle_input():
    while True:
        if keyboard.is_pressed("w"):
            signaling.send_input("w")
        if mouse.is_pressed(button='left'):
            signaling.send_input("left_click")
        await asyncio.sleep(0.01)



async def main():
    await asyncio.gather(
        run_client(),
        handle_input()
    )

asyncio.run(main())
