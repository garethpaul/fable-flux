import unittest
import asyncio
from unittest.mock import AsyncMock, call, patch

import aiohttp

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

    def test_model_validation_accepts_only_http_200(self):
        client = PoeClient(api_key="test-key", config={"models": ["test-model"]})

        for status, expected in (
            (200, True),
            (201, False),
            (302, False),
            (401, False),
            (403, False),
            (429, False),
            (500, False),
        ):
            with self.subTest(status=status):
                response = FakePoeResponse(status, "private upstream details")
                result = asyncio.run(client._process_validation_response(response, "test-model"))
                self.assertIs(expected, result)

    def test_timeout_retry_sleeps_once_and_exhausted_attempt_returns_immediately(self):
        client = PoeClient(api_key="test-key", config={"models": ["test-model"]})
        client.session = object()
        client._make_request = AsyncMock(side_effect=[asyncio.TimeoutError(), None])

        with patch("src.poe_client.asyncio.sleep", new_callable=AsyncMock) as sleep:
            result = asyncio.run(client.generate_story("prompt", max_retries=1))

        self.assertIsNone(result)
        self.assertEqual(2, client._make_request.await_count)
        self.assertEqual([call(5)], sleep.await_args_list)

    def test_rate_limit_retry_uses_provider_backoff_once(self):
        client = PoeClient(api_key="test-key", config={"models": ["test-model"]})
        client.session = object()
        rate_limit_error = aiohttp.ClientResponseError(None, (), status=429)
        client._make_request = AsyncMock(side_effect=[rate_limit_error, "story"])

        with patch("src.poe_client.asyncio.sleep", new_callable=AsyncMock) as sleep:
            result = asyncio.run(client.generate_story("prompt", max_retries=1))

        self.assertEqual("story", result)
        self.assertEqual(2, client._make_request.await_count)
        self.assertEqual([call(60)], sleep.await_args_list)


if __name__ == "__main__":
    unittest.main()
