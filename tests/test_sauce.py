import unittest

from retroasset.sauce import Sauce, decode_sauce, encode_sauce


class SauceTests(unittest.TestCase):
    def test_round_trip(self):
        payload = b"HELLO"
        meta = Sauce(
            title="RetroAsset",
            author="Ploos AS",
            group="Test",
            date="20261006",
            tinfo1=80,
            tinfo2=25,
        )
        blob = payload + encode_sauce(meta, len(payload))
        decoded, found = decode_sauce(blob)
        self.assertEqual(decoded, payload)
        self.assertEqual(found, meta)
        self.assertEqual(len(blob) - len(payload), 128)

    def test_missing_sauce(self):
        payload, meta = decode_sauce(b"ANSI")
        self.assertEqual(payload, b"ANSI")
        self.assertIsNone(meta)


if __name__ == "__main__":
    unittest.main()
