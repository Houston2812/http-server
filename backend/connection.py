class Connection(object):
    def __init__(self, connection, requests = [], responses = []) -> None:
        self.connection = connection
        self.index = 0
        self.requests = requests
        self.responses = responses

    def add_request(self, request):
        self.requests.insert(0, request)
        # self.requests.append(request)

    def add_response(self, responses):
        for response in responses:
            self.responses.insert(0, response)

    def get_first_response(self):
        return self.responses[0]

    def remove_response(self):
        self.responses = self.responses[1:]

    def remove_request(self):
        self.requests = self.requests[1:]
        
    def get_first_request(self):
        request = self.requests[0]
        self.requests = self.requests[1:]
        self.index -= 1
        
        return request
    

        
