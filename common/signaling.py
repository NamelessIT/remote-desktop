import asyncio

async def send(data):
    with open("signal.txt", "w") as f:
        f.write(data.sdp)

async def receive():
    while True:
        try:
            with open("signal.txt", "r") as f:
                sdp = f.read()
                if sdp:
                    return sdp
        except:
            await asyncio.sleep(0.1)


def send_input(input_data):
    with open("input.txt", "w") as f:
        f.write(input_data)
