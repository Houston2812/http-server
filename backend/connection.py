import time 

TIMEOUT = 60 

class Connection(object):
    """
        Connection class that handles all parameters of a single connection.
        Parameters:
            * requests - keeps track of incoming requests
            * partial_request - keeps track of the partial request
            * responses - keep track of the responses for the requests
            * connection - client socket
            * timer - timer that handles timeouts
            * file_descriptor - file descriptor of the socket 
    """
    def __init__(self, connection, file_descriptor, requests = [], responses = []) -> None:
        self.requests = requests
        self.partial_request = ''
        self.responses = responses
        self.connection = connection
        self.timer = time.perf_counter()
        self.file_descriptor = file_descriptor

    def add_request(self, request):
        self.requests.insert(0, request)

    def add_response(self, responses):
        for response in responses:
            self.responses.insert(0, response)

    def get_response(self):
        return self.responses[-1]

    def remove_response(self):
        self.responses.pop()

    def remove_request(self):
        self.requests.pop()

    def check_timeout(self):
        now = time.perf_counter()

        timeout_counter = abs(self.timer - now)
        
        if timeout_counter > TIMEOUT:
            if len(self.requests) == 0 and len(self.responses) == 0:
                return False
            else:
                self.connection.send(b'')
                return True
        else:
            return True

    

        
