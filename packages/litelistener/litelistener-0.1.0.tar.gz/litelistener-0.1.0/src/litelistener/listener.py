from liteclient.client import LiteClient


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
