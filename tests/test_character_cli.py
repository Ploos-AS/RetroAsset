import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CharacterCliTests(unittest.TestCase):
    def test_ansi_json_round_trip(self):
        source = {
            "columns": 2,
            "rows": 1,
            "cells": [
                {"codepoint": 65, "foreground": 7, "background": 0, "blink": False},
                {"codepoint": 219, "foreground": 15, "background": 1, "blink": False},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "asset.json"
            ans = root / "asset.ans"
            restored = root / "restored.json"
            src.write_text(json.dumps(source), encoding="utf-8")
            subprocess.run([sys.executable, "-m", "retroasset.cli", "char-export", str(src),
                            "--target", "ansi-cp437", "-o", str(ans)], check=True)
            subprocess.run([sys.executable, "-m", "retroasset.cli", "char-import", str(ans),
                            "--target", "ansi-cp437", "--columns", "2", "--rows", "1",
                            "-o", str(restored)], check=True)
            self.assertEqual(json.loads(restored.read_text(encoding="utf-8")), source)


    def test_ansi_sauce_round_trip_and_geometry(self):
        source = {
            "columns": 2,
            "rows": 1,
            "cells": [
                {"codepoint": 65, "foreground": 7, "background": 0, "blink": False},
                {"codepoint": 66, "foreground": 7, "background": 0, "blink": False},
            ],
            "sauce": {
                "title": "RetroAsset",
                "author": "Ploos AS",
                "group": "Test",
                "date": "20261006",
                "data_type": 1,
                "file_type": 1,
                "tinfo1": 2,
                "tinfo2": 1,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "asset.json"
            ans = root / "asset.ans"
            restored = root / "restored.json"
            src.write_text(json.dumps(source), encoding="utf-8")
            subprocess.run([sys.executable, "-m", "retroasset.cli", "char-export", str(src),
                            "--target", "ansi-cp437", "-o", str(ans)], check=True)
            subprocess.run([sys.executable, "-m", "retroasset.cli", "char-import", str(ans),
                            "--target", "ansi-cp437", "-o", str(restored)], check=True)
            self.assertEqual(json.loads(restored.read_text(encoding="utf-8")), source)


    def test_c64_native_exports(self):
        cells = [
            {"screen_code": (i % 64), "color": (i % 16)}
            for i in range(1000)
        ]
        source = {"columns": 40, "rows": 25, "cells": cells}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "c64.json"
            src.write_text(json.dumps(source), encoding="utf-8")
            expected_sizes = {"screen": 1000, "color": 1000}
            for fmt, size in expected_sizes.items():
                out = root / fmt
                subprocess.run([sys.executable, "-m", "retroasset.cli", "char-export", str(src),
                                "--target", "c64-screen", "--format", fmt, "-o", str(out)], check=True)
                self.assertEqual(out.stat().st_size, size)
            prg = root / "viewer.prg"
            subprocess.run([sys.executable, "-m", "retroasset.cli", "char-export", str(src),
                            "--target", "c64-screen", "--format", "prg", "-o", str(prg)], check=True)
            self.assertGreater(prg.stat().st_size, 2000)


if __name__ == "__main__":
    unittest.main()
