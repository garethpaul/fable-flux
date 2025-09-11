"""
Main Story Generator
Orchestrates the entire story generation process with diversity tracking and quality control
"""

import json
import yaml
import random
import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import glob

from .diversity_tracker import DiversityTracker
from .poe_client import PoeClient
from .story_validator import StoryValidator

class StoryGenerator:
    """
    Main story generation orchestrator
    """
    
    def __init__(self, config_path: str = "config/generation_config.yaml"):
        """
        Initialize the story generator with configuration
        """
        self.config = self._load_config(config_path)
        self.diversity_tracker = DiversityTracker()
        self.validator = StoryValidator(self.config.get('quality', {}))
        
        # Load generation data
        self.characters = self._load_json_data(self.config['paths']['characters_file'])
        self.settings = self._load_json_data(self.config['paths']['settings_file'])
        self.tags = self._load_json_data(self.config['paths']['tags_file'])
        
        # Load existing stories for inspiration
        self.existing_stories = self._load_existing_stories()
        
        # Initialize Poe client
        self.poe_client = None
        
        # Setup logging
        self._setup_logging()
        
        # Load or initialize progress tracking
        self.progress_file = self.config['paths']['progress_file']
        self.progress = self._load_progress()
        
        logging.info(f"Story generator initialized with {len(self.characters)} characters, "
                    f"{len(self.settings)} settings, {len(self.tags)} tags")
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logging.info(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            logging.error(f"Failed to load config from {config_path}: {e}")
            raise
            
    def _load_json_data(self, filepath: str) -> List[str]:
        """Load JSON data and extract the main list"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                # Find the main data list
                for key in ['characters', 'settings', 'tags']:
                    if key in data:
                        return data[key]
                # If no standard key found, use the first list value
                for value in data.values():
                    if isinstance(value, list):
                        return value
            elif isinstance(data, list):
                return data
                
            raise ValueError(f"No suitable data list found in {filepath}")
            
        except Exception as e:
            logging.error(f"Failed to load data from {filepath}: {e}")
            raise
            
    def _load_existing_stories(self) -> List[str]:
        """Load existing stories for inspiration"""
        stories = []
        stories_dir = self.config['paths']['existing_stories']
        
        try:
            story_files = glob.glob(os.path.join(stories_dir, "*.md"))
            logging.info(f"Found {len(story_files)} existing story files")
            
            # Load a sample of stories (to avoid memory issues)
            sample_size = min(200, len(story_files))
            selected_files = random.sample(story_files, sample_size)
            
            for filepath in selected_files:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    stories.append(content)
                except Exception as e:
                    logging.warning(f"Failed to load story {filepath}: {e}")
                    
        except Exception as e:
            logging.warning(f"Failed to load existing stories: {e}")
            
        logging.info(f"Loaded {len(stories)} existing stories for inspiration")
        return stories
        
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file', 'logs/generation.log')
        
        # Create logs directory if it doesn't exist
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def _load_progress(self) -> Dict:
        """Load progress tracking data"""
        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    progress = json.load(f)
                logging.info(f"Loaded progress: {progress.get('completed_stories', 0)} stories completed")
                return progress
        except Exception as e:
            logging.warning(f"Failed to load progress file: {e}")
            
        return {
            'completed_stories': 0,
            'failed_stories': [],
            'last_story_id': self.config['generation']['start_id'] - 1,
            'start_time': datetime.now().isoformat()
        }
        
    def _save_progress(self):
        """Save progress tracking data"""
        try:
            # Create directory if it doesn't exist
            Path(self.progress_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.progress_file, 'w') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save progress: {e}")
            
    async def initialize_poe_client(self):
        """Initialize the Poe API client with model validation"""
        api_key = os.getenv('POE_API_KEY')
        if not api_key:
            raise ValueError("POE_API_KEY environment variable must be set")
            
        poe_config = self.config.get('poe_api', {})
        
        try:
            self.poe_client = PoeClient(api_key, poe_config)
            logging.info(f"Initialized PoeClient with {len(self.poe_client.available_models)} models: {self.poe_client.available_models}")
        except ValueError as e:
            logging.error(f"Failed to initialize PoeClient due to model configuration error: {e}")
            raise RuntimeError(f"Model configuration error: {e}")
        
        # Test connection and validate models
        logging.info("Testing Poe API connection and validating models...")
        try:
            async with self.poe_client as client:
                if await client.test_connection():
                    logging.info("Poe API connection and model validation successful")
                else:
                    raise RuntimeError("Poe API connection or model validation failed")
        except RuntimeError as e:
            logging.error(f"Model validation failed: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error during client initialization: {e}")
            raise RuntimeError(f"Client initialization failed: {e}")
                
    async def generate_story_batch(self, start_id: int, end_id: int) -> Dict:
        """
        Generate a batch of stories with high concurrency
        
        Args:
            start_id: Starting story ID
            end_id: Ending story ID (inclusive)
            
        Returns:
            Dictionary with batch results
        """
        if not self.poe_client:
            await self.initialize_poe_client()
            
        story_ids = list(range(start_id, end_id + 1))
        batch_results = {
            'total_requested': len(story_ids),
            'successful': 0,
            'failed': 0,
            'failed_ids': []
        }
        
        logging.info(f"Starting concurrent batch generation: stories {start_id} to {end_id} ({len(story_ids)} stories)")
        
        async with self.poe_client:
            # Create concurrent tasks for all stories
            semaphore = asyncio.Semaphore(self.config['generation']['concurrent_requests'])
            tasks = [
                self._generate_story_with_semaphore(story_id, semaphore)
                for story_id in story_ids
            ]
            
            # Process all stories concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for story_id, result in zip(story_ids, results):
                if isinstance(result, Exception):
                    logging.error(f"✗ Exception generating story {story_id}: {result}")
                    batch_results['failed'] += 1
                    batch_results['failed_ids'].append(story_id)
                    self.progress['failed_stories'].append(story_id)
                elif result:
                    batch_results['successful'] += 1
                    self.progress['completed_stories'] += 1
                    self.progress['last_story_id'] = max(self.progress.get('last_story_id', 0), story_id)
                    if batch_results['successful'] % 10 == 0:
                        logging.info(f"✓ Completed {batch_results['successful']}/{batch_results['total_requested']} stories")
                else:
                    batch_results['failed'] += 1
                    batch_results['failed_ids'].append(story_id)
                    self.progress['failed_stories'].append(story_id)
                    
        # Save final progress
        self._save_progress()
        
        success_rate = (batch_results['successful'] / batch_results['total_requested']) * 100
        logging.info(f"Concurrent batch completed: {batch_results['successful']} successful, {batch_results['failed']} failed ({success_rate:.1f}% success rate)")
        return batch_results
        
    async def _generate_story_with_semaphore(self, story_id: int, semaphore: asyncio.Semaphore) -> bool:
        """
        Generate a single story with semaphore control for concurrency limiting
        """
        async with semaphore:
            try:
                return await self.generate_single_story(story_id)
            except Exception as e:
                logging.error(f"Error in semaphore-controlled generation for story {story_id}: {e}")
                return False
        
    async def generate_single_story(self, story_id: int) -> bool:
        """
        Generate a single story with full diversity and quality control
        
        Args:
            story_id: The ID number for the story
            
        Returns:
            True if story was successfully generated and saved, False otherwise
        """
        try:
            # Get systematic selections for diversity
            character = self.diversity_tracker.get_next_character(self.characters)
            setting = self.diversity_tracker.get_next_setting(self.settings)
            tags = self.diversity_tracker.get_balanced_tags(
                self.tags,
                self.config['diversity']['min_tags_per_story'],
                self.config['diversity']['max_tags_per_story']
            )
            story_type = self.diversity_tracker.get_story_type()
            
            # Optionally use existing story as inspiration
            base_story = None
            if (self.existing_stories and 
                random.random() < self.config['generation']['use_existing_inspiration']):
                base_story = random.choice(self.existing_stories)
                logging.debug(f"Using existing story as inspiration for story {story_id}")
                
            # Build generation prompt
            prompt = self.poe_client.build_story_prompt(
                story_id, character, setting, tags, story_type, base_story
            )
            
            # Generate story with retries
            max_attempts = self.config['retry']['max_attempts']
            for attempt in range(max_attempts):
                try:
                    story_content = await self.poe_client.generate_story(prompt)
                    
                    if not story_content:
                        logging.warning(f"Empty response from API for story {story_id}, attempt {attempt + 1}")
                        continue
                        
                    # Validate the generated story
                    is_valid, validation_results = self.validator.validate_story(story_content)
                    
                    if is_valid:
                        # Save the story
                        if await self._save_story(story_id, story_content):
                            # Record successful usage for diversity tracking
                            self.diversity_tracker.record_usage(character, setting, tags, story_type)
                            logging.debug(f"Story {story_id} generated successfully on attempt {attempt + 1}")
                            return True
                        else:
                            logging.error(f"Failed to save story {story_id}")
                            return False
                    else:
                        errors = validation_results.get('errors', [])
                        warnings = validation_results.get('warnings', [])
                        logging.warning(f"Story {story_id} failed validation on attempt {attempt + 1}: {errors}")
                        
                        # For final attempt, log detailed validation results
                        if attempt == max_attempts - 1:
                            logging.error(f"Story {story_id} validation failed after {max_attempts} attempts")
                            logging.error(f"Errors: {errors}")
                            logging.warning(f"Warnings: {warnings}")
                            
                except Exception as e:
                    logging.error(f"Generation attempt {attempt + 1} failed for story {story_id}: {e}")
                    
                # Wait before retry
                if attempt < max_attempts - 1:
                    wait_time = self.config['retry']['backoff_factor'] ** attempt
                    await asyncio.sleep(wait_time)
                    
            return False
            
        except Exception as e:
            logging.error(f"Failed to generate story {story_id}: {e}")
            return False
            
    async def _save_story(self, story_id: int, content: str) -> bool:
        """
        Save generated story to file
        
        Args:
            story_id: Story ID number
            content: Complete story content with frontmatter
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create output directory if it doesn't exist
            output_dir = Path(self.config['paths']['output_directory'])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save story file
            filename = f"story_{story_id:04d}.md"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logging.debug(f"Saved story {story_id} to {filepath}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to save story {story_id}: {e}")
            return False
            
    def get_generation_stats(self) -> Dict:
        """
        Get comprehensive generation statistics including model information
        """
        diversity_stats = self.diversity_tracker.get_usage_stats()
        
        total_target = self.config['generation']['end_id'] - self.config['generation']['start_id'] + 1
        completed = self.progress['completed_stories']
        
        # Model information
        model_info = {
            'configured_models': [],
            'model_count': 0
        }
        
        if self.poe_client:
            model_info = {
                'configured_models': self.poe_client.available_models,
                'model_count': len(self.poe_client.available_models)
            }
        else:
            # Fallback to config if client not initialized
            poe_config = self.config.get('poe_api', {})
            models = poe_config.get('models', poe_config.get('model', ['Unknown']))
            if isinstance(models, str):
                models = [models]
            model_info = {
                'configured_models': models,
                'model_count': len(models) if isinstance(models, list) else 1
            }
        
        stats = {
            'progress': {
                'completed_stories': completed,
                'total_target': total_target,
                'completion_percentage': (completed / total_target * 100) if total_target > 0 else 0,
                'failed_stories': len(self.progress.get('failed_stories', [])),
                'last_story_id': self.progress.get('last_story_id', 0)
            },
            'diversity': diversity_stats,
            'configuration': {
                'start_id': self.config['generation']['start_id'],
                'end_id': self.config['generation']['end_id'],
                'batch_size': self.config['generation']['batch_size'],
                'characters_count': len(self.characters),
                'settings_count': len(self.settings),
                'tags_count': len(self.tags)
            },
            'models': model_info
        }
        
        return stats
        
    async def retry_failed_stories(self) -> Dict:
        """
        Retry generation for previously failed stories
        """
        failed_ids = self.progress.get('failed_stories', [])
        if not failed_ids:
            logging.info("No failed stories to retry")
            return {'total_retried': 0, 'successful': 0, 'still_failed': 0}
            
        logging.info(f"Retrying {len(failed_ids)} failed stories")
        
        if not self.poe_client:
            await self.initialize_poe_client()
            
        results = {'total_retried': len(failed_ids), 'successful': 0, 'still_failed': 0}
        still_failed = []
        
        async with self.poe_client:
            for story_id in failed_ids:
                success = await self.generate_single_story(story_id)
                if success:
                    results['successful'] += 1
                    logging.info(f"✓ Retry successful for story {story_id}")
                else:
                    results['still_failed'] += 1
                    still_failed.append(story_id)
                    logging.error(f"✗ Retry failed for story {story_id}")
                    
        # Update failed stories list
        self.progress['failed_stories'] = still_failed
        self._save_progress()
        
        return results

# Convenience function for simple batch generation
async def generate_stories(start_id: int, end_id: int, config_path: str = "config/generation_config.yaml") -> Dict:
    """
    Simple function to generate a batch of stories
    """
    generator = StoryGenerator(config_path)
    return await generator.generate_story_batch(start_id, end_id)