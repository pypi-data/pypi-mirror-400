from time import sleep
from liteclient.client import LiteClient

POLL_INTERVAL = 2


def poll(
    handlers: dict,
    host: str,
    port: int,
    target_keys: list,
    poll_interval: int = POLL_INTERVAL,
):
    """
    Blocks and listens for data. When data is found, it calls 'callback(key, data)'.
    """
    client = LiteClient(host, port)
    print(f"[*] Listener active. Watching: {target_keys}")

    try:
        while True:
            # RPOP returns [key_name, value]
            for key in target_keys:
                result = client.rpop(key)

                if result:
                    # Execute the external logic passed into this function
                    handler = handlers.get(key)
                    if handler:
                        handler(result)
                    else:
                        print(f"[?] No handler registered for key: {key}")
            sleep(poll_interval)

    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        client.close()


# This only works if the server (litequeue) implements a blpop command handler
# which it currently does not -- I will add that later -- its more complex than
# just polling with the client -- I want to move along with other development
# so will come back to that later
def listen(handlers: dict, host: str, port: int, target_keys: list):
    """
    Blocks and listens for data. When data is found, it calls 'callback(key, data)'.
    """
    client = LiteClient(host, port)
    print(f"[*] Listener active. Watching: {target_keys}")

    try:
        while True:
            # BLPOP returns [key_name, value]
            result = client.blpop(target_keys, timeout=0)
            if result:
                key_name, data = result
                # Execute the external logic passed into this function
                handler = handlers.get(key_name)
                if handler:
                    handler(data)
                else:
                    print(f"[?] No handler registered for key: {key_name}")
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    finally:
        client.close()
