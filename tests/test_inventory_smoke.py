"""Offline smoke tests for the current inventory desktop prototype.

No GUI is displayed; the module loads against an isolated temporary SQLite DB.
These tests do NOT certify the password hashing implementation as secure.
"""
import hashlib
import importlib.util
import os
import sqlite3
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
                # inventory.py closes its module-level connection after
                # import; reopen the temporary DB only for inspection.
                with sqlite3.connect(Path(temp) / "inventory.db") as conn:
                    names = {
                        row[0] for row in conn.execute(
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
