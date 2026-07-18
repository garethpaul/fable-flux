import tempfile
import unittest
from pathlib import Path

from src.huggingface_uploader import StoryParser


class StoryParserTests(unittest.TestCase):
    def write_story(self, content):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "story_1.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_parse_story_file_accepts_mapping_frontmatter(self):
        path = self.write_story("""---
id: story_1
type: daily_adventure
characters: ["Milo"]
setting: garden
words: 12
tags: ["kindness"]
---

# Milo Shares

Milo shared a pail with a friend.

The End.""")

        record = StoryParser().parse_story_file(path)

        self.assertIsNotNone(record)
        self.assertEqual("story_1", record["id"])
        self.assertEqual(["Milo"], record["characters"])
        self.assertEqual(["kindness"], record["tags"])

    def test_parse_story_file_rejects_non_mapping_frontmatter(self):
        path = self.write_story("""---
- not
- metadata
---

# Milo Shares

Milo shared a pail with a friend.

The End.""")

        self.assertIsNone(StoryParser().parse_story_file(path))

    def test_parse_story_file_rejects_scalar_sequence_metadata(self):
        path = self.write_story("""---
id: story_1
type: daily_adventure
characters: Milo
setting: garden
words: 12
tags: kindness
---

# Milo Shares

Milo shared a pail with a friend.

The End.""")

        self.assertIsNone(StoryParser().parse_story_file(path))

    def test_parse_story_file_rejects_non_string_sequence_items(self):
        path = self.write_story("""---
id: story_1
type: daily_adventure
characters: ["Milo", 7]
setting: garden
words: 12
tags: ["kindness"]
---

# Milo Shares

Milo shared a pail with a friend.

The End.""")

        with self.assertLogs(level="WARNING") as captured:
            self.assertIsNone(StoryParser().parse_story_file(path))
        # Observe the guard's own diagnostic, not just the None result: the
        # outer `except Exception` in parse_story_file also returns None when a
        # removed guard lets an incidental AttributeError escape, so asserting
        # None alone passes whether or not the guard exists.
        self.assertTrue(
            any(
                "must contain only non-empty strings" in message
                for message in captured.output
            ),
            captured.output,
        )

    def test_parse_story_file_rejects_invalid_scalar_metadata_types(self):
        replacements = {
            "id: story_1": "id: [story_1]",
            "setting: garden": "setting: [garden]",
            "words: 12": "words: false",
        }

        for original, replacement in replacements.items():
            with self.subTest(replacement=replacement):
                path = self.write_story("""---
id: story_1
type: daily_adventure
characters: ["Milo"]
setting: garden
words: 12
tags: ["kindness"]
---

# Milo Shares

Milo shared a pail with a friend.

The End.""".replace(original, replacement))

                self.assertIsNone(StoryParser().parse_story_file(path))

    def test_parse_story_file_rejects_invalid_story_type(self):
        path = self.write_story("""---
id: story_1
type: scary_tale
characters: ["Milo"]
setting: garden
words: 12
tags: ["kindness"]
---

# Milo Shares

Milo shared a pail with a friend.

The End.""")

        self.assertIsNone(StoryParser().parse_story_file(path))


if __name__ == "__main__":
    unittest.main()
