"""Test public Flask pages with a synthetic session key and no external services."""
import os
import unittest
from unittest.mock import patch

class PublicPagesTests(unittest.TestCase):
    def test_public_pages_and_contact(self):
        with patch.dict(os.environ, {"SECRET_KEY": "ci-only-not-a-real-secret"}, clear=True):
            import run
            run.app.config.update(TESTING=True, SECRET_KEY="ci-only-not-a-real-secret")
            client = run.app.test_client()
            for path in ("/", "/about", "/careers", "/contact"):
                self.assertEqual(client.get(path).status_code, 200, path)
            response = client.post("/contact", data={"name": "<script>alert(1)</script>"})
            self.assertEqual(response.status_code, 200)
            self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", response.get_data(as_text=True))
    def test_debugger_is_disabled(self):
        from pathlib import Path
        import ast
        tree = ast.parse(Path("run.py").read_text())
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "run"]
        self.assertTrue(calls)
        for call in calls:
            self.assertFalse(next(ast.literal_eval(x.value) for x in call.keywords if x.arg == "debug"))
