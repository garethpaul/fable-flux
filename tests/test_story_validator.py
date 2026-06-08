import unittest

import src.story_validator as story_validator
from src.story_validator import StoryValidator


def story_with_body(words):
    return """---
id: story_1
type: daily_adventure
characters: ["Milo"]
setting: garden
words: 58
tags: ["kindness", "friendship"]
---

# Milo Shares The Garden

{words}

The End.""".format(words=words)


class StoryValidatorTests(unittest.TestCase):
    def setUp(self):
        self.original_textstat = story_validator.HAS_TEXTSTAT
        self.original_textblob = story_validator.HAS_TEXTBLOB
        story_validator.HAS_TEXTSTAT = False
        story_validator.HAS_TEXTBLOB = False

    def tearDown(self):
        story_validator.HAS_TEXTSTAT = self.original_textstat
        story_validator.HAS_TEXTBLOB = self.original_textblob

    def validator(self):
        return StoryValidator({
            "min_words": 40,
            "max_words": 90,
            "required_sentiment_score": -1.0,
            "min_reading_ease": 0,
        })

    def test_validate_story_accepts_well_formed_frontmatter_and_content(self):
        content = story_with_body(
            "Milo saw a friend by the gate. Milo smiled and shared a bright red pail. "
            "They planted seeds, added water, and waited together. The garden felt warm "
            "and safe. When a tiny sprout appeared, Milo learned that kind work and "
            "patient friends can help small things grow. They cleaned their tools, waved "
            "goodbye, and promised to care for the tiny sprout every sunny morning."
        )

        is_valid, results = self.validator().validate_story(content)

        self.assertTrue(is_valid, results)
        self.assertEqual([], results["errors"])

    def test_missing_frontmatter_is_invalid(self):
        is_valid, results = self.validator().validate_story("# Story\n\nThe End.")

        self.assertFalse(is_valid)
        self.assertIn("Invalid story structure", results["errors"][0])

    def test_invalid_story_type_is_reported(self):
        content = story_with_body(
            "Milo and friends learn kindness together. " * 12
        ).replace("type: daily_adventure", "type: scary_tale")

        is_valid, results = self.validator().validate_story(content)

        self.assertFalse(is_valid)
        self.assertTrue(any("Invalid story type" in error for error in results["errors"]))


if __name__ == "__main__":
    unittest.main()
