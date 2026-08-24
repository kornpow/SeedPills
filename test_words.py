#!/usr/bin/env python3
"""Verify the abbreviated SCAD words against the canonical BIP39 list."""

import json
import re
import unittest
import urllib.request
from pathlib import Path


BIP39_ENGLISH_URL = (
    "https://raw.githubusercontent.com/bitcoin/bips/master/"
    "bip-0039/english.txt"
)
SCAD = Path(__file__).with_name("seeds.scad")


class WordListTest(unittest.TestCase):
    def test_scad_words_match_bip39_english(self):
        source = SCAD.read_text(encoding="utf-8")
        match = re.search(r"(?ms)^words\s*=\s*(\[.*?\])\s*;", source)
        self.assertIsNotNone(match, "could not find words = [...] in seeds.scad")
        scad_words = json.loads(match.group(1))

        with urllib.request.urlopen(BIP39_ENGLISH_URL, timeout=30) as response:
            bip39_words = response.read().decode("utf-8").splitlines()
        expected = [word[:4].upper() for word in bip39_words]

        self.assertEqual(len(scad_words), 2048)
        self.assertEqual(scad_words, expected)


if __name__ == "__main__":
    unittest.main()
