import json
import os
import tempfile
import unittest
from pathlib import Path

from app.evals.io import read_json, write_json_atomic, get_mengram_version


class EvalsIOTest(unittest.TestCase):
    def test_write_read_roundtrip(self):
        data = {"a": 1}
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "out.json"
            write_json_atomic(data, p)
            loaded = read_json(p)
            self.assertEqual(loaded, data)

    def test_malformed_json_error(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text("{bad", encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                read_json(p)
            self.assertIn(str(p), str(ctx.exception))
            self.assertIn("line", str(ctx.exception))

    def test_get_version(self):
        ver = get_mengram_version()
        self.assertTrue(isinstance(ver, str))


if __name__ == "__main__":
    unittest.main()
