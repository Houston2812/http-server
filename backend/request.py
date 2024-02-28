class Request:
    def __init__(self, HttpMethod, HttpURI, Host) -> None:
        self.HttpMethod = HttpMethod
        self.HttpURI = HttpURI
        self.Host = Host

    