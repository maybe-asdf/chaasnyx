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
log("Importing asyncio and sys")
import asyncio
import sys
log("Importing json and toml")
import json
import toml
log("Importing websockets")
from websockets.asyncio.server import serve
log("Finished importing")
clients = set()
senders = set()
user_map = {} 
with open("server.config") as f:
     config = toml.loads(f.read())
admins = config["roles"]["admin"]
mods = config["roles"]["mod"]
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
    user_map[sender_name] = websocket
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
            if message_content[0] == ">":
                command = message_content.split(" ")
                if command[0]== ">list":
                    await websocket.send(json.dumps({"sender": "SERVER", "content": str(senders)}))
                elif command[0] == ">help":
                    await websocket.send(json.dumps({"sender": "SERVER", "content": "Commands:"}))
                    await websocket.send(json.dumps({"sender": "SERVER", "content": ">msg username content- messages another user"}))
                    await websocket.send(json.dumps({"sender": "SERVER", "content": ">list - lists all active users"}))
                    await websocket.send(json.dumps({"sender": "SERVER", "content": ">stop - stops the server (only can be used by admins)"}))
                    await websocket.send(json.dumps({"sender": "SERVER", "content": ">kick username - kicks someone (only can be used by moderators)"}))
                elif command[0] == ">kick":
                                if sender in mods and len(command) > 1:
                                    target = command[1]
                                    target_ws = user_map.get(target)
                                    if target_ws:
                                        await target_ws.send("You have been kicked.")
                                        await target_ws.close()
                                        log(f"{sender} kicked {target}")
                                    else:
                                        await websocket.send(json.dumps({"sender": "SERVER", "content": "User not found."}))
                                else:
                                    await websocket.send(json.dumps({"sender": "SERVER", "content": "Usage: >kick username (only can be used by mods)"}))
                elif command[0] == ">msg":
                    if len(command) < 3:
                        await websocket.send(json.dumps({"sender": "SERVER", "content": "Usage: >msg username message"}))
                    else:
                        target = command[1]
                        msg = " ".join(command[2:])
                        target_ws = user_map.get(target)
                        if target_ws:
                            await target_ws.send(json.dumps({"sender": f"[whisper from {sender}]", "content": msg}))
                            await websocket.send(json.dumps({"sender": f"[you -> {target}]", "content": msg}))
                        else:
                            await websocket.send(json.dumps({"sender": "SERVER", "content": "User not found"}))
                elif command[0] == ">stop":
                    if sender in admins:
                        for client in clients.copy():
                            try:
                                await client.send(json.dumps({"sender": "SERVER", "content": "Server stopping!"}))
                            except:
                                clients.discard(websocket)
                                senders.discard(sender_name)
                                user_map.pop(sender_name, None)
                    else:
                        await client.send(json.dumps({"sender": "SERVER", "content": "Who do you think you are? Insufficient permissions."}))
                else:
                    await websocket.send(json.dumps({"sender": "SERVER", "content": "Unknown command. Try >help"}))
            else:
                for client in clients.copy():
                    try:
                        await client.send(json.dumps({"sender": sender, "content": message_content}))
                    except:
                        clients.discard(websocket)
                        senders.discard(sender_name)
                        user_map.pop(sender_name, None)
    finally:
        clients.discard(websocket)
        senders.discard(sender_name)
        user_map.pop(sender_name, None)
        for client in clients.copy():
                try:
                    await client.send(f"- {sender_name} - just left -")
                except:
                    clients.discard(websocket)
                    senders.discard(sender_name)
                    user_map.pop(sender_name, None)
async def main():
    log("Open for business!")
    async with serve(handler, "0.0.0.0", 6741):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
