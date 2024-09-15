def get_username():

    username = input("Please enter your desired username: ")


    username = username.strip()


    username = username.upper()


    return username



if __name__ == "__main__":
    print("Your username is:", get_username())


def get_group():

    group_name = input("Please enter the group name you'd like to join: ")


    group_name = group_name.strip()


    group_name = group_name.upper()


    return group_name



if __name__ == "__main__":
    print("The group name is:", get_group())


def get_message():

    message = input("Please enter the message you'd like to send: ")


    message = message.strip()


    return message



if __name__ == "__main__":
    print("The message is:", get_message())


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

    n.start()
    return n

def join_group(p2p):
    """
    Joins a specified group using the given node.
    """
    p2p.join(p2p)
    print(f"Joined group: {p2p}")

def chat_task(pipe, n, p2p):
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
            n.shouts(p2p, message.decode('utf-8'))
        else:
            cmds = n.recv()
            msg_type = cmds.pop(0).decode('utf-8')
            uuid.UUID(bytes=cmds.pop(0))
            peer_username = cmds.pop(0).decode('utf-8')
            match msg_type:
                case "SHOUT":
                    intended_group = cmds.pop(0).decode('utf-8')
                    if intended_group == p2p:

                        print(f"{peer_username}: {cmds.pop(0).decode('utf-8')}")
                case "ENTER":
                    json.loads(cmds.pop(0).decode('utf-8'))

                    print( f"{peer_username}: is now connected." )
                case "JOIN":

                    print( f"{peer_username}: joined {cmds.pop( 0 ).decode( 'utf-8' )}." )

    n.stop()

def get_channel(noodle, P2P):
    """
    Starts a chat task in a new ZeroMQ thread for a specified group.
    """
    ctx = zmq.Context()
    return zhelper.zthread_fork(ctx, chat_task, n=noodle, group=P2P)


from chat_helpers import get_peer_node, join_group, get_channels


if __name__ == "__main__":

    username = "example_user"
    group = "example_group"


    node = get_peer_node(username)


    join_group(node, group)


    channel = get_channels(node, group)


    print("Chat channel created:", channel)


import chat_helpers as ch


if __name__ == "__main__":

    username = "example_user"
    group = "example_group"


    node = ch.get_peer_node(username)


    ch.join_group(node, group)


    channel = ch.get_channel(node, group)


    print("Chat channel created:", channel)


import chat_helpers as ch


if __name__ == "__main__":

    username = "example_user"
    group = "example_group"


    node = ch.get_peer_node(username)


    ch.join_group(node, group)


    channel = ch.get_channel(node, group)


    print("Chat channel created:", channel)
# main_script.py

import lab_chat as lc


if __name__ == "__main__":

    username = "example_user"
    group = "example_group"


    node = lc.get_peer_node(username)


    lc.join_group(node, group)


    channel = lc.get_channel(node, group)


    print("Chat channel created:", channel)

# !/usr/bin/env python3

from lab_chat import get_peer_node, join_group, get_channel
import zmq


def get_username():
    """
    Prompt the user for their desired username, clean it, and convert to uppercase.

    Returns:
    - str: The processed username in uppercase.
    """
    username = input("Please enter your desired username: ")
    username = username.strip().upper()
    return username


def get_group():
    """
    Prompt the user for the group name they want to join, clean it, and convert to uppercase.

    Returns:
    - str: The processed group name in uppercase.
    """
    group_name = input("Please enter the group name you'd like to join: ")
    group_name = group_name.strip().upper()
    return group_name


def get_message():
    """
    Prompt the user for the message they want to send and clean it.

    Returns:
    - str: The cleaned message.
    """
    message = input("Please enter the message you'd like to send: ")
    message = message.strip()
    return message


def main():

    username = get_username()
    group = get_group()


    node = get_peer_node(username)


    join_group(node, group)


    channel = get_channel(node, group)

    print("Chat channel created:", channel)


    try:
        while True:
            message = get_message()
            if message == "$$STOP":
                break

            node.shouts(group, message)
    except KeyboardInterrupt:
        print("\nChat ended.")


if __name__ == "__main__":
    main()



