import unittest
import asyncio

from src.poe_client import PoeClient, RateLimiter


class FakePoeResponse:
    def __init__(self, status, body):
        self.status = status
        self._body = body

    async def text(self):
        return self._body


class FakeClock:
    def __init__(self):
        self.current = 0.0
        self.sleeps = []

    def now(self):
        return self.current

    async def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.current += seconds


class PoeClientTests(unittest.TestCase):
    def test_rate_limiter_rejects_invalid_limits(self):
        with self.assertRaisesRegex(ValueError, "Rate limit must be positive"):
            RateLimiter(rate=0)

        with self.assertRaisesRegex(ValueError, "Rate limit period must be positive"):
            RateLimiter(rate=1, per=0)

    def test_rate_limiter_rechecks_token_after_waiting(self):
        clock = FakeClock()
        limiter = RateLimiter(rate=1, per=10.0, clock=clock.now, sleep=clock.sleep)

        asyncio.run(limiter.acquire())
        self.assertEqual([], clock.sleeps)
        self.assertEqual(0.0, limiter.allowance)

        asyncio.run(limiter.acquire())

        self.assertEqual([5.0, 5.0], clock.sleeps)
        self.assertEqual(10.0, clock.current)
        self.assertEqual(0.0, limiter.allowance)

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

    def test_response_body_summary_omits_raw_response_content(self):
        summary = PoeClient._response_body_summary("private generated story")

        self.assertEqual("23 characters", summary)
        self.assertNotIn("private", summary)
        self.assertNotIn("story", summary)

    def test_model_validation_logs_response_summary_without_raw_body(self):
        client = PoeClient(api_key="test-key", config={"models": ["test-model"]})
        response = FakePoeResponse(400, '{"error":"invalid model private details"}')

        with self.assertLogs(level="WARNING") as context:
            result = asyncio.run(client._process_validation_response(response, "test-model"))

        logs = "\n".join(context.output)
        self.assertFalse(result)
        self.assertIn("Poe validation response body omitted from logs", logs)
        self.assertIn("41 characters", logs)
        self.assertNotIn("private details", logs)


if __name__ == "__main__":
    unittest.main()
