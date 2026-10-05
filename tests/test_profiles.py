import unittest

from retroasset.profiles import get_profile


class ProfileTests(unittest.TestCase):
    def test_amiga_profiles(self):
        self.assertEqual(get_profile("amiga-ocs").max_colors, 32)
        self.assertEqual(get_profile("amiga-aga").max_colors, 256)

    def test_ansi_profile(self):
        profile = get_profile("ansi-cp437")
        self.assertEqual(profile.family, "character")
        self.assertEqual(profile.columns, 80)
        self.assertEqual(profile.charset, "cp437")


if __name__ == "__main__":
    unittest.main()
