# peer_chat.py

from pyre import Pyre
from pyre import zhelper
import zmq
import uuid
import json

def get_peer_node(username):
    """
    Creates and starts a Pyre node for the given username.
    """
    n = Pyre(username)
    # Uncomment and configure if needed
    # n.set_header("CHAT_Header1", "example header1")
    # n.set_header("CHAT_Header2", "example header2")
    n.start()
    return n

def join_group(node, group):
    """
    Joins a specified group using the given node.
    """
    node.join(group)
    print(f"Joined group: {group}")

def chat_task(ctx, pipe, n, group):
    """
    Handles the chat functionality for a given group.
    """
    poller = zmq.Poller()
    poller.register(pipe, zmq.POLLIN)
    poller.register(n.socket(), zmq.POLLIN)

    while True:
        items = dict(poller.poll())
        if pipe in items and items[pipe] == zmq.POLLIN:
            message = pipe.recv()
            if message.decode('utf-8') == "$$STOP":
                break
            print(f"YOU: {message.decode('utf-8')}")
            n.shouts(group, message.decode('utf-8'))
        else:
            cmds = n.recv()
            msg_type = cmds.pop(0).decode('utf-8')
            peer_id = uuid.UUID(bytes=cmds.pop(0))
            peer_username = cmds.pop(0).decode('utf-8')
            match msg_type:
                case "SHOUT":
                    intended_group = cmds.pop(0).decode('utf-8')
                    if intended_group == group:
                        print(f"{peer_username}: {cmds.pop(0).decode('utf-8')}")
                case "ENTER":
                    headers = json.loads(cmds.pop(0).decode('utf-8'))
                    print(f"{peer_username}: is now connected.")
                case "JOIN":
                    print(f"{peer_username}: joined {cmds.pop(0).decode('utf-8')}.")
    n.stop()

def get_channel(node, group):
    """
    Starts a chat task in a new ZeroMQ thread for a specified group.
    """
    ctx = zmq.Context()
    return zhelper.zthread_fork(ctx, chat_task, n=node, group=group)
