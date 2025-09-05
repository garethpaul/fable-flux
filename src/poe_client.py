"""
Poe API Client for Story Generation
Handles API communication with rate limiting and retry logic
"""

import aiohttp
import asyncio
import json
import logging
import time
from typing import Optional, Dict, Any
from asyncio import Semaphore
import os

class RateLimiter:
    """Simple rate limiter using token bucket algorithm"""
    
    def __init__(self, rate: int, per: float = 60.0):
        self.rate = rate  # requests per time period
        self.per = per    # time period in seconds
        self.allowance = rate
        self.last_check = time.time()
        
    async def acquire(self):
        """Wait until we can make a request"""
        current = time.time()
        time_passed = current - self.last_check
        self.last_check = current
        
        # Add tokens based on time passed
        self.allowance += time_passed * (self.rate / self.per)
        if self.allowance > self.rate:
            self.allowance = self.rate
            
        if self.allowance < 1.0:
            # Need to wait
            sleep_time = (1.0 - self.allowance) * (self.per / self.rate)
            await asyncio.sleep(sleep_time)
            self.allowance = 0.0
        else:
            self.allowance -= 1.0

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
        
        # Configuration
        self.model = self.config.get('model', 'GPT-5')
        self.temperature = self.config.get('temperature', 0.7)
        self.max_tokens = self.config.get('max_tokens', 1200)
        self.top_p = self.config.get('top_p', 0.9)
        self.timeout = self.config.get('timeout', 30)
        
        # Rate limiting
        rate_limit = self.config.get('rate_limit', 10)
        self.rate_limiter = RateLimiter(rate_limit, 60.0)
        self.semaphore = Semaphore(self.config.get('concurrent_requests', 5))
        
        # Session will be created when needed
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
            
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
                try:
                    story_content = await self._make_request(prompt)
                    if story_content:
                        logging.debug(f"Successfully generated story on attempt {attempt + 1}")
                        return story_content
                        
                except aiohttp.ClientResponseError as e:
                    if e.status == 429:  # Rate limited
                        wait_time = min(60 * (2 ** attempt), 300)  # Exponential backoff, max 5 min
                        logging.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                        continue
                    elif e.status == 401:  # Authentication error
                        logging.error(f"Authentication failed: {e}")
                        return None
                    else:
                        logging.error(f"HTTP error {e.status}: {e}")
                        
                except asyncio.TimeoutError:
                    wait_time = 5 * (attempt + 1)
                    logging.warning(f"Request timeout, waiting {wait_time}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logging.info(f"Retrying in {wait_time}s (attempt {attempt + 2}/{max_retries + 1})")
                    await asyncio.sleep(wait_time)
                    
        logging.error(f"Failed to generate story after {max_retries + 1} attempts")
        return None
        
    async def _make_request(self, prompt: str) -> Optional[str]:
        """
        Make the actual API request
        """
        payload = {
            "model": self.model,
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
            "max_tokens": self.max_tokens,
            "top_p": self.top_p
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with self.session.post(self.base_url, json=payload, headers=headers) as response:
            response.raise_for_status()
            
            result = await response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                logging.debug(f"Generated content length: {len(content)} characters")
                return content
            else:
                logging.error(f"Unexpected API response format: {result}")
                return None
                
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
        Test the API connection with a simple request
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
                result = await self.generate_story(test_prompt, max_retries=1)
                if result and "test_001" in result:
                    logging.info("API connection test successful")
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