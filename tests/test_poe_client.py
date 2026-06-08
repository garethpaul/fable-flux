import unittest

from src.poe_client import PoeClient


class PoeClientTests(unittest.TestCase):
    def test_poe_client_rejects_empty_model_list(self):
        with self.assertRaisesRegex(ValueError, "Models array cannot be empty"):
            PoeClient(api_key="test-key", config={"models": []})

    def test_build_story_prompt_contains_required_yaml_shape(self):
        client = PoeClient(api_key="test-key", config={"models": ["test-model"]})

        prompt = client.build_story_prompt(
            story_id=42,
            character="Milo",
            setting="garden",
            tags=["kindness", "friendship"],
            story_type="daily_adventure",
        )

        self.assertIn("id: story_42", prompt)
        self.assertIn('characters: ["Milo"]', prompt)
        self.assertIn('tags: ["kindness", "friendship"]', prompt)
        self.assertIn("The End.", prompt)


if __name__ == "__main__":
    unittest.main()
