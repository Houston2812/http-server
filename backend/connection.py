import time 

TIMEOUT = 60 

class Connection(object):
    def __init__(self, connection, file_descriptor, requests = [], responses = []) -> None:
        self.index = 0
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
        
        # if timeout_counter > TIMEOUT / 10:
        #     if timeout_counter <= TIMEOUT:
        #         print(f"[!] Timeout countdown: {int(TIMEOUT - timeout_counter):2}s", end='\r')

        if timeout_counter > TIMEOUT:
            return False
        else:
            return True
        
    def get_first_request(self):
        request = self.requests[0]
        self.requests = self.requests[1:]
        self.index -= 1
        
        return request
    

        
