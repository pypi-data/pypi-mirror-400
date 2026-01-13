class KeyringSecretProvider:
    def __init__(self, service: str) -> None:
        self.service = service

    def get(self, key: str):
        return None
