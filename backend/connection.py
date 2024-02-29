class Connection(object):
    def __init__(self, file_descriptor, connection, request, response) -> None:
        self.file_descriptor = file_descriptor
        self.connection = connection
        self.request = request
        self.response = response

    

        
