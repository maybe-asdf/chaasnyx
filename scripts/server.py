ver = "v000002"
print(fr"""
      __                               
 ____/ /  ___ ____ ____ ___  __ ____ __
/ __/ _ \/ _ `/ _ `(_-</ _ \/ // /\ \ /
\__/_//_/\_,_/\_,_/___/_//_/\_, //_\_\ 
      {ver} server         /___/       
      """)
def log(thing):
    print(thing)
log("Importing asyncio")
import asyncio
log("Importing json")
import json
log("Importing websockets")
from websockets.asyncio.server import serve
log("Finished importing")
clients = set()
senders = set()
log("Defining..")
async def handler(websocket):
    join_msg_string = await websocket.recv()
    join_msg = json.loads(join_msg_string)

    sender_name = join_msg["sender"]
    if join_msg["content"] != "join;":
        log(f"Someone tried to log in without a valid content. Denied access")
        await websocket.send("Invalid authentication/username. We are done here")
        return

    if sender_name in senders:
        log(f"Someone tried to log in by the taken username of {sender_name}. Denied access")
        await websocket.send("Taken username. We are done here")
        return

    senders.add(sender_name)
    clients.add(websocket)

    # join message
    for client in clients.copy():
        try:
            await client.send(f"- {sender_name} - just joined -")
        except:
            clients.discard(client)
            senders.discard(sender_name)

    try:
        async for message_string in websocket:
            message = json.loads(message_string)
            message_content = message["content"]
            sender = message["sender"]

            for client in clients.copy():
                try:
                    await client.send(json.dumps({"sender": sender, "content": message_content}))
                except:
                    clients.discard(client)
                    senders.discard(sender)
    finally:
        clients.discard(websocket)
        senders.discard(sender_name)
        for client in clients.copy():
                try:
                    await client.send(f"- {sender_name} - just left -")
                except:
                    clients.discard(client)
                    senders.discard(sender_name)
async def main():
    log("Open for business!")
    async with serve(handler, "0.0.0.0", 6741):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
