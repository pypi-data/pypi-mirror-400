import os


class EnvSecretProvider:
    def get(self, key: str):
        return os.getenv(key)
