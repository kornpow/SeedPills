import json
import unittest
from pathlib import Path


ROOT = Path(__file__).parent


class ProjectVersionTest(unittest.TestCase):
    def test_version_is_visible_in_readme_and_preset(self):
        version = (ROOT / "VERSION").read_text().strip()
        readme = (ROOT / "README.md").read_text()
        preset = json.loads(
            (ROOT / "presets/SeedPills 0.20mm @BBL P1S.json").read_text()
        )

        self.assertIn(version, readme)
        self.assertIn(version, preset["name"])
        self.assertIn(version, preset["print_settings_id"])
        self.assertIn(version, preset["description"])


if __name__ == "__main__":
    unittest.main()
