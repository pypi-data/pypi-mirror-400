class APIResponseError(Exception):
    def __init__(self, message: str, status_code: int, payload: str):
        self.message = message
        self.status_code = status_code
        self.payload = payload
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} [{self.status_code}]. Payload={self.payload}"
