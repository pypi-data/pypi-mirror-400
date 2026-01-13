import time

import jwt


class AuthToken:
    def __init__(self, secret_key: str, algorithms="HS256"):
        self.secret_key = secret_key.strip()
        self.algorithms = algorithms

    def generate(self, data: dict, expired_seconds: int = 300) -> str:
        payload = data
        payload["exp"] = int(time.time()) + expired_seconds
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithms);

    def retrieve(self, token: str, verify_signature=True, algorithms=None):
        if verify_signature:
            payload = jwt.decode(token.strip(), self.secret_key,
                                 algorithms=self.algorithms if algorithms is None else algorithms)
        else:
            payload = jwt.decode(token.strip(), options={"verify_signature": False},
                                 algorithms=self.algorithms if algorithms is None else algorithms)
        del payload["exp"]
        return payload

    def generate_auth_headers(self, data: dict, expired_seconds: int = 300) -> str:
        payload = data
        payload["exp"] = int(time.time()) + expired_seconds

        gateway_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.generate(data, expired_seconds)}"
        }

        return gateway_headers;
