"""
Poe API Client for Story Generation
Handles API communication with rate limiting and retry logic
"""

import aiohttp
import asyncio
import json
import logging
import time
import random
from typing import Optional, Dict, Any, List
from asyncio import Semaphore
import os


MAX_POE_RESPONSE_BYTES = 1024 * 1024
POE_RESPONSE_CHUNK_BYTES = 64 * 1024


class PoeResponseTooLarge(ValueError):
    pass

class RateLimiter:
    """High-performance rate limiter using token bucket algorithm for concurrent requests"""
    
    def __init__(self, rate: int, per: float = 60.0, clock=time.monotonic, sleep=asyncio.sleep):
        if rate <= 0:
            raise ValueError("Rate limit must be positive")
        if per <= 0:
            raise ValueError("Rate limit period must be positive")

        self.rate = rate  # requests per time period
        self.per = per    # time period in seconds
        self.allowance = float(rate)
        self._clock = clock
        self._sleep = sleep
        self.last_check = self._clock()
        self._lock = asyncio.Lock()  # Protect against race conditions in concurrent access
        
        # Pre-calculate for efficiency
        self.tokens_per_second = self.rate / self.per
        self.seconds_per_token = self.per / self.rate
        
    async def acquire(self):
        """Wait until we can make a request (thread-safe for concurrent use)"""
        while True:
            async with self._lock:
                current = self._clock()
                time_passed = max(0.0, current - self.last_check)
                self.last_check = current
                
                # Add tokens based on time passed
                self.allowance = min(
                    float(self.rate),
                    self.allowance + time_passed * self.tokens_per_second,
                )
                
                if self.allowance >= 1.0:
                    self.allowance -= 1.0
                    return  # Request can proceed immediately

                sleep_time = (1.0 - self.allowance) * self.seconds_per_token

            if sleep_time > 0:
                await self._sleep(min(sleep_time, 5.0))  # Cap sleep time for responsiveness

class PoeClient:
    """
    Async client for Poe API with rate limiting and error handling
    """
    
    def __init__(self, api_key: str = None, config: Dict[str, Any] = None):
        self.api_key = api_key or os.getenv('POE_API_KEY')
        if not self.api_key:
            raise ValueError("POE_API_KEY must be provided or set as environment variable")
            
        self.config = config or {}
        self.base_url = "https://api.poe.com/v1/chat/completions"
        
        # Model configuration with validation
        self.available_models = self._validate_and_get_models()
        self.temperature = self.config.get('temperature', 0.7)
        self.timeout = self.config.get('timeout', 30)
        
        # Rate limiting
        rate_limit = self.config.get('rate_limit', 10)
        self.rate_limiter = RateLimiter(rate_limit, 60.0)
        self.semaphore = Semaphore(self.config.get('concurrent_requests', 5))
        
        # Session will be created when needed
        self.session = None
        
    def _validate_and_get_models(self) -> List[str]:
        """
        Validate and extract models from configuration
        
        Returns:
            List of validated model names
            
        Raises:
            ValueError: If no models are configured or models list is empty
        """
        # Check for both 'models' (array) and 'model' (single) for backward compatibility
        models = self.config.get('models')
        single_model = self.config.get('model')
        
        if models is not None:
            if not isinstance(models, list):
                raise ValueError("'models' configuration must be a list/array")
            if len(models) == 0:
                raise ValueError("Models array cannot be empty. At least one model must be specified.")
            
            # Validate each model name
            valid_models = []
            for model in models:
                if not isinstance(model, str) or not model.strip():
                    logging.warning(f"Skipping invalid model: {model}")
                    continue
                valid_models.append(model.strip())
            
            if len(valid_models) == 0:
                raise ValueError("No valid models found in configuration. All model names were invalid.")
                
            logging.info(f"Configured with {len(valid_models)} models: {valid_models}")
            return valid_models
            
        elif single_model:
            # Backward compatibility for single model configuration
            if not isinstance(single_model, str) or not single_model.strip():
                raise ValueError("Single model configuration must be a non-empty string")
            logging.info(f"Using single model configuration: {single_model}")
            return [single_model.strip()]
            
        else:
            # Default fallback
            default_model = 'GPT-5'
            logging.warning(f"No models configured, using default: {default_model}")
            return [default_model]
    
    def select_random_model(self) -> str:
        """
        Randomly select a model from the available models
        
        Returns:
            Randomly selected model name
        """
        if not self.available_models:
            raise RuntimeError("No available models to select from")
            
        selected_model = random.choice(self.available_models)
        logging.debug(f"Selected model: {selected_model} from {self.available_models}")
        return selected_model

    @staticmethod
    def _response_body_summary(response_text: str) -> str:
        """Describe an upstream response without logging its raw content."""
        return f"{len(response_text or '')} characters"

    @staticmethod
    async def _read_response_text(response) -> str:
        """Read one Poe response within the fixed decoded-byte boundary."""
        content_length = response.content_length
        if content_length is not None and content_length > MAX_POE_RESPONSE_BYTES:
            raise PoeResponseTooLarge("Poe response exceeds the 1 MiB limit")

        body = bytearray()
        async for chunk in response.content.iter_chunked(POE_RESPONSE_CHUNK_BYTES):
            if len(body) + len(chunk) > MAX_POE_RESPONSE_BYTES:
                raise PoeResponseTooLarge("Poe response exceeds the 1 MiB limit")
            body.extend(chunk)

        return bytes(body).decode("utf-8", errors="strict")
    
    async def validate_model_accessibility(self, model: str) -> bool:
        """
        Validate that a specific model is accessible via the API
        
        Args:
            model: Model name to validate
            
        Returns:
            True if model is accessible, False otherwise
        """
        test_payload = {
            "model": model,
            "messages": [{"role": "user", "content": "test"}],
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Always use the session if available, create temporary one if not
            if self.session:
                async with self.session.post(self.base_url, json=test_payload, headers=headers) as response:
                    return await self._process_validation_response(response, model)
            else:
                # Create a properly managed temporary session
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as temp_session:
                    async with temp_session.post(self.base_url, json=test_payload, headers=headers) as response:
                        return await self._process_validation_response(response, model)
                        
        except Exception as e:
            logging.warning(f"Failed to validate model {model}: {e}")
            return False
    
    async def _process_validation_response(self, response, model: str) -> bool:
        """Process validation response consistently"""
        try:
            if response.status == 200:
                logging.debug(f"Model {model} is accessible")
                return True
            elif response.status == 400:
                response_text = await self._read_response_text(response)
                error_msg = response_text.lower()
                if 'model' in error_msg or 'invalid' in error_msg:
                    logging.warning(
                        f"Model {model} is not accessible; Poe validation response body omitted from logs "
                        f"({self._response_body_summary(response_text)})"
                    )
                    return False
                logging.warning(
                    f"Model {model} returned 400 error; Poe validation response body omitted from logs "
                    f"({self._response_body_summary(response_text)})"
                )
                return False
            elif response.status == 404:
                logging.warning(f"Model {model} not found (404)")
                return False
            else:
                logging.warning(f"Model {model} validation returned status {response.status}")
                return False
        except PoeResponseTooLarge:
            logging.error(f"Poe validation response for {model} exceeded the 1 MiB limit")
            return False
        except UnicodeDecodeError:
            logging.error(f"Poe validation response for {model} was not valid UTF-8; body omitted")
            return False
        except Exception as e:
            logging.error(f"Error processing validation response for {model}: {e}")
            return False
    
    async def validate_all_models(self) -> Dict[str, bool]:
        """
        Validate accessibility of all configured models
        
        Returns:
            Dictionary mapping model names to their accessibility status
        """
        results = {}
        for model in self.available_models:
            results[model] = await self.validate_model_accessibility(model)
            
        accessible_count = sum(results.values())
        logging.info(f"Model validation results: {accessible_count}/{len(results)} models accessible")
        
        if accessible_count == 0:
            raise RuntimeError("No configured models are accessible via the API")
            
        return results
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with proper cleanup"""
        if self.session:
            try:
                await self.session.close()
                logging.debug("HTTP session closed successfully")
            except Exception as e:
                logging.warning(f"Error closing HTTP session: {e}")
            finally:
                self.session = None
            
    async def generate_story(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        Generate a story using the Poe API with retry logic
        
        Args:
            prompt: The generation prompt
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated story content or None if failed
        """
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with PoeClient()' pattern")
            
        async with self.semaphore:  # Limit concurrent requests
            await self.rate_limiter.acquire()  # Rate limiting
            
            for attempt in range(max_retries + 1):
                retry_delay = 2 ** attempt
                try:
                    story_content = await self._make_request(prompt)
                    if story_content:
                        logging.debug(f"Successfully generated story on attempt {attempt + 1}")
                        return story_content
                        
                except aiohttp.ClientResponseError as e:
                    if e.status == 429:  # Rate limited
                        retry_delay = min(60 * (2 ** attempt), 300)
                        logging.warning(f"Rate limited on attempt {attempt + 1}")
                    elif e.status == 401:  # Authentication error
                        logging.error(f"Authentication failed: {e}")
                        return None
                    else:
                        logging.error(f"HTTP error {e.status}: {e}")
                        
                except asyncio.TimeoutError:
                    retry_delay = 5 * (attempt + 1)
                    logging.warning(f"Request timeout on attempt {attempt + 1}")
                    
                except Exception as e:
                    logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    
                if attempt < max_retries:
                    logging.info(f"Retrying in {retry_delay}s (attempt {attempt + 2}/{max_retries + 1})")
                    await asyncio.sleep(retry_delay)
                    
        logging.error(f"Failed to generate story after {max_retries + 1} attempts")
        return None
        
    async def _make_request(self, prompt: str) -> Optional[str]:
        """
        Make the actual API request with randomly selected model
        """
        # Select a random model for this request
        selected_model = self.select_random_model()
        
        payload = {
            "model": selected_model,
            "messages": [
                {
                    "role": "system",
                    "content": """You are a skilled children's story writer who creates educational, positive stories for children aged 3 and up.

Your stories should:
- Be engaging and fun for young children
- Include clear educational messages
- Use simple, age-appropriate language
- Include dialogue and sensory details
- End with positive resolutions
- Follow the exact format requested

Always follow the exact YAML frontmatter format and story structure provided in the prompt."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": self.temperature,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        logging.debug(f"Making request with model: {selected_model}")
        
        try:
            async with self.session.post(self.base_url, json=payload, headers=headers) as response:
                response_text = await self._read_response_text(response)
                
                if response.status == 200:
                    try:
                        result = json.loads(response_text)
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']
                            logging.debug(f"Generated content length: {len(content)} characters with model {selected_model}")
                            return content
                        else:
                            logging.error(
                                "Unexpected API response format from %s; response body omitted (%s)",
                                selected_model,
                                self._response_body_summary(response_text),
                            )
                            return None
                            
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse JSON response from {selected_model}: {e}")
                        logging.error(
                            "Poe response body omitted from logs; length: "
                            f"{self._response_body_summary(response_text)}"
                        )
                        return None
                        
                elif response.status == 400:
                    logging.error(
                        "HTTP 400 Bad Request with model %s; response body length: %s",
                        selected_model,
                        self._response_body_summary(response_text),
                    )
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"Bad Request with model {selected_model}"
                    )
                    
                else:
                    logging.error(
                        "HTTP %s error with model %s; response body length: %s",
                        response.status,
                        selected_model,
                        self._response_body_summary(response_text),
                    )
                    response.raise_for_status()
                    
        except PoeResponseTooLarge:
            logging.error(f"Poe response from {selected_model} exceeded the 1 MiB limit")
            return None
        except UnicodeDecodeError:
            logging.error(f"Poe response from {selected_model} was not valid UTF-8; body omitted")
            return None
        except aiohttp.ClientResponseError:
            raise  # Re-raise HTTP errors
        except Exception as e:
            logging.error(f"Unexpected error making request with model {selected_model}: {e}")
            raise
                
    def build_story_prompt(self, story_id: int, character: str, setting: str, 
                          tags: list, story_type: str, base_story: str = None) -> str:
        """
        Build the complete generation prompt for the API
        
        Args:
            story_id: The story ID number
            character: Main character for the story
            setting: Setting for the story
            tags: List of educational tags/themes
            story_type: Either "problem_solution" or "daily_adventure"
            base_story: Optional existing story to use as inspiration
            
        Returns:
            Complete prompt string
        """
        primary_theme = tags[0] if tags else "friendship"
        key_values = ", ".join(tags[:3])
        tags_json = json.dumps(tags)
        
        base_prompt = f"""Create a children's story with these exact specifications:

CHARACTER: {character}
SETTING: {setting}
STORY TYPE: {story_type}
THEMES/TAGS: {', '.join(tags)}
TARGET AGE: 3+ years
WORD COUNT: 600-700 words
TONE: Positive, educational, encouraging

Requirements:
- Include YAML frontmatter with exact metadata format
- Focus on {primary_theme} as the main lesson
- Use simple, age-appropriate language suitable for 3-year-olds
- Include dialogue and sensory details  
- End with a positive resolution and clear lesson
- Ensure the story promotes {key_values}
- Make it engaging and fun for young children
- The story should teach children valuable life lessons

Format the output EXACTLY like this example:
---
id: story_{story_id}
type: {story_type}
characters: ["{character}"]
setting: {setting}
words: [actual_word_count]
tags: {tags_json}
---

# [Creative Story Title]

[Story content here with proper paragraphs, dialogue, and age-appropriate vocabulary. Make sure to include sensory details, emotions, and a clear learning journey for the main character. The story should be engaging for 3-year-olds while teaching important values.]

The End."""

        if base_story:
            # Truncate base story to avoid token limits
            truncated_story = base_story[:1000] + "..." if len(base_story) > 1000 else base_story
            
            inspiration_text = f"""

Use this existing story as inspiration for themes and emotional structure, but create a completely NEW story with the specified character and setting:

INSPIRATION STORY:
{truncated_story}

Adapt the core lesson and emotional journey, but create fresh characters, plot, and details. Do not copy any specific elements - use it only for thematic inspiration."""
            
            base_prompt += inspiration_text
            
        return base_prompt
        
    async def test_connection(self) -> bool:
        """
        Test the API connection and validate model accessibility
        """
        test_prompt = """Create a very short test story (50 words) about a happy cat in a garden.

Format:
---
id: test_001
type: daily_adventure
characters: ["happy cat"]
setting: garden
words: [actual_word_count]
tags: ["happiness", "nature"]
---

# Test Story

[Short story content]

The End."""

        try:
            async with self:
                # First validate all configured models
                validation_results = await self.validate_all_models()
                accessible_models = [model for model, accessible in validation_results.items() if accessible]
                
                if not accessible_models:
                    logging.error("No accessible models found during connection test")
                    return False
                
                logging.info(f"Found {len(accessible_models)} accessible models: {accessible_models}")
                
                # Test story generation with a random model
                result = await self.generate_story(test_prompt, max_retries=1)
                if result and "test_001" in result:
                    logging.info("API connection and model validation successful")
                    return True
                else:
                    logging.error("API connection test failed - invalid response")
                    return False
                    
        except Exception as e:
            logging.error(f"API connection test failed: {e}")
            return False

# Convenience function for simple usage
async def generate_single_story(api_key: str, prompt: str, config: Dict[str, Any] = None) -> Optional[str]:
    """
    Generate a single story with a simple function call
    """
    async with PoeClient(api_key, config) as client:
        return await client.generate_story(prompt)
