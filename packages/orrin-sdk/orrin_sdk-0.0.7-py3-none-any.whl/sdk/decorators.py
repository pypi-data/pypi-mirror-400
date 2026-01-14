import inspect
import pathlib
import requests, sys

API_BASE = "https://stellr-company.com"

class OrrinSDK:
    def __init__(self, developer_api_key: str):
        self.developer_api_key = developer_api_key
        self._registered_actions = []  # store action metadata
        self._source_file = None       # the file we will read later

    def action(self, name: str, extra_metadata: dict = {}):
        """
        Decorator to mark a function as a platform action.
        Stores metadata but does not upload yet.
        """
        def decorator(fn):
            # Track the source file (once)
            if self._source_file is None:
                try:
                    self._source_file = pathlib.Path(inspect.getfile(fn))
                except Exception:
                    pass

            # Save action metadata
            action_data = {
                "action_name": name,
                "entrypoint": fn.__name__,
                "runtime": "python",
                "extra_metadata": extra_metadata or None
            }
            self._registered_actions.append(action_data)

            return fn
        return decorator

    def finalize(self):
        """
        Read the full source file and send all registered actions
        in one request to the backend.
        """
        if not self._registered_actions:
            print("[stellr-sdk] No actions registered, skipping upload.")
            return

        if not self._source_file or not self._source_file.exists():
            print("[stellr-sdk] Could not find source file.")
            return

        try:
            full_source = self._source_file.read_text()
            lines = full_source.splitlines()
            full_source = '\n'.join([
                l for l in lines
                if not l.strip().startswith("from orrinsdk") and 'import OrrinSDK' in l and "OrrinSDK" not in l and not '.action' in l and not '.finalize' in l
            ])
            print(full_source, self._registered_actions)
            sys.exit(0)
        except Exception as e:
            print(f"[stellr-sdk] Failed to read source file: {e}")
            return

        payload = {
            "source_code": full_source,
            "actions": self._registered_actions
        }

        try:
            response = requests.post(
                f"{API_BASE}/actions/register",
                json=payload,
                headers={
                    "Authorization": self.developer_api_key,
                    "fsdk": "yes"
                },
                timeout=10
            )
            if response.status_code == 200:
                print("[stellr-sdk] Actions registered successfully!")
            else:
                print(f"[stellr-sdk] Failed to register actions: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[stellr-sdk] Exception when sending actions: {e}")
