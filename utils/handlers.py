def data_handler(connections: dict, file_descriptor) -> str:
    # receive data of the client
    client_data: bytes = b''

    try:
        while True:
            client_data += connections[file_descriptor].recv(BUF_SIZE)
            
            # if 0 bytes received, it means client stopped sending
            if  len(client_data) == 0:
                break
    except BlockingIOError:
        pass

    return client_data.decode()

def resource_handler(uri: str) -> bytes:
    msg = b''
    with open(uri, 'rb') as response_file:
        msg = response_file.read()

    return msg

def get_handler(request: Request, ):
    pass
