class AIAPIAdapter:
    api_key: str

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def send_request(self, prompt: str) -> str:
        pass