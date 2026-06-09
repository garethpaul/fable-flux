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


if __name__ == "__main__":
    unittest.main()
