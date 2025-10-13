import asyncio
import json
import websockets
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import PromptSession

ver = "v000002"
print(fr"""
      __                               
 ____/ /  ___ ____ ____ ___  __ ____ __
/ __/ _ \/ _ `/ _ `(_-</ _ \/ // /\ \ /
\__/_//_/\_,_/\_,_/___/_//_/\_, //_\_\ 
      {ver} client         /___/       
      """)

async def send_loop(websocket, username, session):
    while True:
        msg_text = await session.prompt_async(f"[{username}] - ")  # no prompt character
        message = {"sender": username, "content": msg_text}
        await websocket.send(json.dumps(message))

async def receive_loop(websocket, username):
    while True:
        try:
            response = await websocket.recv()
            try:
                # Try parsing as JSON
                message = json.loads(response)
                # Skip messages sent by self
                if message.get("sender") == username:
                    continue
                sender = message.get("sender")
                content = message.get("content")
                print(f"[{sender}] - {content}")
            except json.JSONDecodeError:
                # Plain text from server (like join notifications)
                print(response)
        except websockets.ConnectionClosed:
            print("Connection closed")
            break

async def main():
    address = input("ip to connect : ")
    x = address.split(":")
    uri = f"ws://{address}" if len(x) == 2 else f"ws://{address}:6741"
    username = input("username to log in as : ")

    async with websockets.connect(uri) as websocket:
        # Send join message
        join_msg = {"sender": username, "content": "join;"}
        await websocket.send(json.dumps(join_msg))

        session = PromptSession()
        with patch_stdout():  # ensures prints from receive_loop don't break input
            await asyncio.gather(
                send_loop(websocket, username, session),
                receive_loop(websocket, username)
            )

if __name__ == "__main__":
    asyncio.run(main())
