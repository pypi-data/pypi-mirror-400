import ast
import inspect
import pathlib
import requests
import sys

API_BASE = 'http://192.168.1.153:8080'  # "https://stellr-company.com"

class OrrinSDK:
    def __init__(self, developer_api_key: str, app_name: str, desc: str):
        self.developer_api_key = developer_api_key
        self._registered_actions = []  # store action metadata
        self._source_file = None  # the file we will read later
        self.app_name = app_name
        self.description = desc

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
        Read the full source file, strip Orrin-related code using AST (or fallback to line-based),
        and send all registered actions in one request to the backend.
        """
        if not self._registered_actions:
            print("[orrin-sdk] No actions registered, skipping upload.")
            return
        if not self._source_file or not self._source_file.exists():
            print("[orrin-sdk] Could not find source file.")
            return

        try:
            full_source = self._source_file.read_text()
            # Try AST-based stripping first (more robust)
            stripped_source = self._strip_with_ast(full_source)
        except Exception as e:
            print(f"[orrin-sdk] AST stripping failed ({e}), falling back to line-based.")
            stripped_source = self._strip_with_lines(full_source)

        if not stripped_source:
            print("[orrin-sdk] Stripped source is empty, aborting.")
            return

        payload = {
            'app_name': self.app_name,
            'desc': self.description,
            'source_code': stripped_source,
            'actions': self._registered_actions
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
                print(f"[orrin-sdk] Actions registered successfully!\n\nApproval Status: PENDING\nApp ID (remember this, you will need it in your next.js code!):\n\t{response.json()['AppID']}\n\nAll changes, or new apps, must be approved after being submitted. This can take 1-3 days.")
            else:
                print(f"[orrin-sdk] Failed to register actions: {response.status_code} {response.json()['Message']}")
        except Exception as e:
            print(f"[orrin-sdk] Exception when sending actions: {e}")

    def _strip_with_ast(self, source: str) -> str:
        """
        Use AST to parse and remove OrrinSDK-related nodes, then unparse back to source.
        Handles various styles: aliases, multiline, etc.
        """
        tree = ast.parse(source)

        class OrrinRemover(ast.NodeTransformer):
            def visit_Import(self, node):
                # Remove imports like 'import orrinsdk' or aliases
                if any(alias.name == 'orrinsdk' for alias in node.names):
                    return None
                return node

            def visit_ImportFrom(self, node):
                # Remove 'from sdk import OrrinSDK' or 'from orrinsdk import OrrinSDK' (handle module variations)
                if node.module in {'sdk', 'orrinsdk'} and any(alias.name == 'OrrinSDK' for alias in node.names):
                    return None
                return node

            def visit_Assign(self, node):
                # Remove assignments like 'orrin_sdk = OrrinSDK(...)'
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'OrrinSDK':
                    return None
                # Handle if assigned to different var names? For now, assume standard 'OrrinSDK' class name.
                return node

            def visit_Expr(self, node):
                # Remove standalone calls like 'orrin_sdk.finalize()'
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == 'finalize':
                    return None
                return node

            def visit_FunctionDef(self, node):
                # Remove decorators like '@orrin_sdk.action(...)'
                new_decorators = []
                for dec in node.decorator_list:
                    if not (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute) and dec.func.attr == 'action'):
                        new_decorators.append(dec)
                node.decorator_list = new_decorators
                return self.generic_visit(node)

        remover = OrrinRemover()
        cleaned_tree = remover.visit(tree)
        ast.fix_missing_locations(cleaned_tree)
        return ast.unparse(cleaned_tree).strip()

    def _strip_with_lines(self, source: str) -> str:
        """
        Fallback: Original line-based stripping, but improved to handle 'from sdk' and case-insensitivity.
        """
        lines = source.splitlines()
        filtered = []
        for l in lines:
            stripped_l = l.strip().lower()
            if (stripped_l.startswith("from sdk") or stripped_l.startswith("from orrinsdk") or
                stripped_l.startswith("import sdk") or stripped_l.startswith("import orrinsdk")):
                continue
            if 'orrinsdk' in stripped_l or '.action' in stripped_l or '.finalize' in stripped_l:
                continue
            filtered.append(l)
        return '\n'.join(filtered).strip()