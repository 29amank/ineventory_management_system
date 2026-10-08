"""Offline smoke tests for the current inventory desktop prototype.

No GUI is displayed; the module loads against an isolated temporary SQLite DB.
These tests do NOT certify the password hashing implementation as secure.
"""
import hashlib
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "inventory.py"


class TestInventorySmoke(unittest.TestCase):
    def test_first_import_creates_only_temporary_schema(self):
        with tempfile.TemporaryDirectory() as temp:
            cwd = os.getcwd()
            app = None
            try:
                os.chdir(temp)
                spec = importlib.util.spec_from_file_location("inventory_smoke", SOURCE)
                app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app)
                names = {
                    row[0] for row in app.conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
                self.assertIn("products", names)
                self.assertIn("users", names)
                self.assertTrue((Path(temp) / "inventory.db").is_file())
                # Document existing behavior; it needs an adaptive salted hash
                # before real account storage.
                self.assertEqual(
                    app.hash_password("synthetic-password"),
                    hashlib.sha256(b"synthetic-password").hexdigest(),
                )
            finally:
                if app is not None and hasattr(app, "conn"):
                    app.conn.close()
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
