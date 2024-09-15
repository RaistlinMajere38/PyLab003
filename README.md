def get_peer_node(username):
    """
    Creates and starts a Pyre node for the given username.

    Parameters:
    - username (str): The username for which the Pyre node is to be created.

    Returns:
    - Pyre: The Pyre node instance associated with the given username.

    Description:
    This function initializes a `Pyre` node with the provided username, starts the node, 
    and returns the initialized node instance. The node is used for communication and 
    may have various headers set for identifying or configuring the node.
    """
    n = Pyre(username)
    #n.set_header("CHAT_Header1","example header1")
    #n.set_header("CHAT_Header2","example header2")
    n.start()
    return n
def join_group(node, group):
    """
    Joins a specified group using the given node.

    Parameters:
    - node (Pyre): The Pyre node instance that will join the group.
    - group (str): The name of the group to join.

    Returns:
    - None: This function does not return any value.

    Description:
    This function instructs the given `Pyre` node to join the specified group and 
    prints a confirmation message indicating that the group has been joined.
    """
    node.join(group)
    print(f"Joined group: {group}")
def chat_task(ctx, pipe, n, group):
    """
    Handles the chat functionality for a given group, managing incoming and outgoing messages.

    Parameters:
    - ctx (zmq.Context): The ZeroMQ context used for creating sockets and handling messages.
    - pipe (zmq.Socket): The ZeroMQ socket used for receiving messages from the pipe.
    - n (Pyre): The Pyre node instance handling the chat communication.
    - group (str): The group name to which messages are sent and received.

    Returns:
    - None: This function does not return any value.

    Description:
    This function sets up a ZeroMQ poller to monitor both the pipe and the Pyre node's 
    socket for incoming messages. It processes messages based on their type, handling 
    chat messages, user joins, and user status updates. The function continues to run 
    in a loop until a quit command is received. After completion, it stops the Pyre node.
    """
    poller = zmq.Poller()
    poller.register(pipe, zmq.POLLIN)
    # print(n.socket())
    poller.register(n.socket(), zmq.POLLIN)
    # print(n.socket())
    while(True):
        items = dict(poller.poll())
        # print(n.socket(), items)
        if pipe in items and items[pipe] == zmq.POLLIN:
            message = pipe.recv()
            # message to quit
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
                        # print(f"{peer_username}({peer_id}): {cmds}")
                        print(f"{peer_username}: {cmds.pop(0).decode('utf-8')}")
                case "ENTER":
                    headers = json.loads(cmds.pop(0).decode('utf-8'))
                    # print(f"NODE_MSG HEADERS: {headers}")
                    # for key in headers:
                    #    print("key = {0}, value = {1}".format(key, headers[key]))
                    # print( f"{peer_username}({peer_id}): is now connected." )
                    print( f"{peer_username}: is now connected." )
                case "JOIN":
                    #print( f"{peer_username}({peer_id}): joined {cmds.pop(0).decode('utf-8')}." )
                    print( f"{peer_username}: joined {cmds.pop( 0 ).decode( 'utf-8' )}." )
            # print(f"NODE_MSG CONT: {cmds}")
    n.stop()
def get_channel(node, group):
    """
    Starts a chat task in a new ZeroMQ thread for a specified group.

    Parameters:
    - node (Pyre): The Pyre node instance that will be used for chat communication.
    - group (str): The name of the group to which the chat task is associated.

    Returns:
    - zmq.Socket: The ZeroMQ socket used for the chat task, created in a new thread.

    Description:
    This function creates a new ZeroMQ context and starts a `chat_task` in a new 
    thread using `zhelper.zthread_fork`. It passes the node and group parameters to 
    the chat task and returns the ZeroMQ socket associated with the chat task.
    """
    ctx = zmq.Context()
    return zhelper.zthread_fork(ctx, chat_task, n=node, group=group)
