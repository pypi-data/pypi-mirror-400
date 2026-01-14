import inspect
import requests

API_BASE = "https://stellr-company.com"
_registered_actions = set()

class OrrinSDK:
    def __init__(self, developer_api_key: str):
        self.developer_api_key = developer_api_key
    
    def action(self, name: str, extra_metadata: dict = {}): # `extra_metadata` will just be extra metadata for the developer
        def decorator(fn):
            if name in _registered_actions:
                return fn  # avoid duplicate registration
            
            _registered_actions.add(name)

            try:
                source = inspect.getsource(fn)
                payload = {
                    "action_name": name,
                    "entrypoint": fn.__name__,
                    "runtime": "python",
                    "source_code": source
                }

                if not extra_metadata == {}:
                    payload['extra_metadata'] = extra_metadata

                requests.post(
                    f"{API_BASE}/actions/register",
                    json=payload,
                    headers={
                        "Authorization": self.developer_api_key,
                        'fsdk': 'yes'
                    },
                    timeout=5  # avoid hanging imports
                )
            except Exception as e:
                print(f"[stellr-sdk] Warning: Failed to register action '{name}': {e}")

            return fn
        return decorator