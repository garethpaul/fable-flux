"""
Batch Processor for Story Generation
Handles large-scale story generation with progress tracking and monitoring
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path

from .story_generator import StoryGenerator

class BatchProcessor:
    """
    Manages batch processing of story generation with monitoring and control
    """
    
    def __init__(self, config_path: str = "config/generation_config.yaml"):
        self.generator = StoryGenerator(config_path)
        self.config = self.generator.config
        self.is_running = False
        self.should_stop = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.start_time = None
        self.batch_stats = []
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logging.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.should_stop = True
        
    async def run_full_generation(self) -> Dict:
        """
        Run the complete story generation process from start_id to end_id
        """
        start_id = self.config['generation']['start_id']
        end_id = self.config['generation']['end_id']
        batch_size = self.config['generation']['batch_size']
        
        logging.info(f"Starting full generation: stories {start_id} to {end_id}")
        logging.info(f"Batch size: {batch_size}")
        logging.info(f"Total stories to generate: {end_id - start_id + 1}")
        
        self.start_time = datetime.now()
        self.is_running = True
        
        # Check if we're resuming from a previous run
        last_completed = self.generator.progress.get('last_story_id', start_id - 1)
        if last_completed >= start_id:
            resume_id = last_completed + 1
            logging.info(f"Resuming from story {resume_id}")
        else:
            resume_id = start_id
            
        total_results = {
            'total_requested': end_id - start_id + 1,
            'total_completed': 0,
            'total_failed': 0,
            'batches_completed': 0,
            'failed_batches': [],
            'start_time': self.start_time.isoformat(),
            'end_time': None
        }
        
        # Process in batches with high concurrency
        current_id = resume_id
        while current_id <= end_id and not self.should_stop:
            batch_end = min(current_id + batch_size - 1, end_id)
            batch_size_actual = batch_end - current_id + 1
            
            batch_start_time = datetime.now()
            logging.info(f"Processing concurrent batch: stories {current_id} to {batch_end} ({batch_size_actual} stories)")
            
            try:
                batch_results = await self.generator.generate_story_batch(current_id, batch_end)
                batch_duration = (datetime.now() - batch_start_time).total_seconds()
                
                # Update totals
                total_results['total_completed'] += batch_results['successful']
                total_results['total_failed'] += batch_results['failed']
                total_results['batches_completed'] += 1
                
                # Calculate performance metrics
                stories_per_second = batch_size_actual / max(batch_duration, 0.1)
                success_rate = (batch_results['successful'] / batch_size_actual) * 100
                
                # Store enhanced batch stats
                self.batch_stats.append({
                    'batch_start': current_id,
                    'batch_end': batch_end,
                    'successful': batch_results['successful'],
                    'failed': batch_results['failed'],
                    'duration_seconds': batch_duration,
                    'stories_per_second': stories_per_second,
                    'success_rate': success_rate,
                    'timestamp': batch_start_time.isoformat()
                })
                
                # Log enhanced progress
                self._log_enhanced_progress(current_id, batch_end, end_id, batch_results, batch_duration, stories_per_second)
                
                if batch_results['failed'] > 0:
                    total_results['failed_batches'].append({
                        'start_id': current_id,
                        'end_id': batch_end,
                        'failed_ids': batch_results['failed_ids']
                    })
                    
            except Exception as e:
                logging.error(f"Batch {current_id}-{batch_end} failed with exception: {e}")
                total_results['failed_batches'].append({
                    'start_id': current_id,
                    'end_id': batch_end,
                    'error': str(e)
                })
                
            current_id = batch_end + 1
            
            # No pause needed with proper rate limiting - let concurrent processing handle the flow
                
        self.is_running = False
        total_results['end_time'] = datetime.now().isoformat()
        
        if self.should_stop:
            logging.info("Generation stopped by user request")
        else:
            logging.info("Full generation completed!")
            
        self._log_final_summary(total_results)
        await self._save_batch_report(total_results)
        
        return total_results
        
    def _log_progress(self, batch_start: int, batch_end: int, total_end: int, batch_results: Dict):
        """Log detailed progress information (legacy method)"""
        self._log_enhanced_progress(batch_start, batch_end, total_end, batch_results, None, None)
        
    def _log_enhanced_progress(self, batch_start: int, batch_end: int, total_end: int, batch_results: Dict,
                             batch_duration: float = None, stories_per_second: float = None):
        """Log enhanced progress information with performance metrics"""
        total_stories = total_end - self.config['generation']['start_id'] + 1
        completed_so_far = batch_end - self.config['generation']['start_id'] + 1
        progress_pct = (completed_so_far / total_stories) * 100
        
        # Calculate ETA
        eta_str = "Unknown"
        if self.start_time and completed_so_far > 0:
            elapsed = datetime.now() - self.start_time
            avg_time_per_story = elapsed.total_seconds() / completed_so_far
            remaining_stories = total_stories - completed_so_far
            eta_seconds = remaining_stories * avg_time_per_story
            eta = datetime.now() + timedelta(seconds=eta_seconds)
            eta_str = eta.strftime("%H:%M:%S")
            
        success_rate = (batch_results['successful'] / (batch_results['successful'] + batch_results['failed'])) * 100 if (batch_results['successful'] + batch_results['failed']) > 0 else 0
        
        # Build performance info
        perf_info = ""
        if batch_duration is not None and stories_per_second is not None:
            perf_info = f" | Speed: {stories_per_second:.1f} stories/sec | Duration: {batch_duration:.1f}s"
        
        logging.info(f"Progress: {completed_so_far}/{total_stories} ({progress_pct:.1f}%) | "
                    f"Batch: {batch_results['successful']}/{batch_results['successful'] + batch_results['failed']} ({success_rate:.1f}%)"
                    f"{perf_info} | ETA: {eta_str}")
                    
    def _log_final_summary(self, results: Dict):
        """Log comprehensive final summary"""
        total_time = datetime.now() - self.start_time if self.start_time else timedelta(0)
        
        success_rate = (results['total_completed'] / results['total_requested']) * 100 if results['total_requested'] > 0 else 0
        
        logging.info("=" * 60)
        logging.info("GENERATION SUMMARY")
        logging.info("=" * 60)
        logging.info(f"Total time: {total_time}")
        logging.info(f"Stories requested: {results['total_requested']}")
        logging.info(f"Stories completed: {results['total_completed']}")
        logging.info(f"Stories failed: {results['total_failed']}")
        logging.info(f"Success rate: {success_rate:.1f}%")
        logging.info(f"Batches completed: {results['batches_completed']}")
        logging.info(f"Failed batches: {len(results['failed_batches'])}")
        
        if results['total_completed'] > 0 and total_time.total_seconds() > 0:
            stories_per_hour = results['total_completed'] / (total_time.total_seconds() / 3600)
            logging.info(f"Average rate: {stories_per_hour:.1f} stories/hour")
            
        # Diversity stats
        diversity_stats = self.generator.diversity_tracker.get_usage_stats()
        if diversity_stats['total_stories'] > 0:
            logging.info(f"Diversity - Character usage range: {diversity_stats['character_usage']['min']}-{diversity_stats['character_usage']['max']}")
            logging.info(f"Diversity - Setting usage range: {diversity_stats['setting_usage']['min']}-{diversity_stats['setting_usage']['max']}")
            logging.info(f"Diversity - Unique tag combinations: {diversity_stats['unique_tag_combinations']}")
            
    async def _save_batch_report(self, results: Dict):
        """Save detailed batch processing report"""
        try:
            report_dir = Path("logs")
            report_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"batch_report_{timestamp}.json"
            
            # Include batch statistics
            results['batch_statistics'] = self.batch_stats
            results['diversity_stats'] = self.generator.diversity_tracker.get_usage_stats()
            
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            logging.info(f"Batch report saved to {report_file}")
            
        except Exception as e:
            logging.error(f"Failed to save batch report: {e}")
            
    async def run_test_batch(self, size: int = 5) -> Dict:
        """
        Run a small test batch to verify everything is working
        """
        start_id = self.config['generation']['start_id']
        end_id = start_id + size - 1
        
        logging.info(f"Running test batch: {size} stories ({start_id} to {end_id})")
        
        # Temporarily initialize if needed
        if not self.generator.poe_client:
            await self.generator.initialize_poe_client()
            
        return await self.generator.generate_story_batch(start_id, end_id)
        
    async def retry_failed_stories(self) -> Dict:
        """
        Retry all previously failed stories
        """
        logging.info("Starting retry process for failed stories...")
        return await self.generator.retry_failed_stories()
        
    def get_current_stats(self) -> Dict:
        """
        Get current generation statistics
        """
        stats = self.generator.get_generation_stats()
        
        # Add runtime information
        if self.start_time:
            runtime = datetime.now() - self.start_time
            stats['runtime'] = {
                'elapsed_seconds': runtime.total_seconds(),
                'elapsed_formatted': str(runtime),
                'is_running': self.is_running
            }
            
        stats['batch_statistics'] = self.batch_stats
        
        return stats
        
    async def monitor_progress(self, update_interval: int = 60):
        """
        Monitor and log progress at regular intervals
        """
        while self.is_running and not self.should_stop:
            stats = self.get_current_stats()
            progress = stats['progress']
            
            logging.info(f"Monitor - Completed: {progress['completed_stories']}, "
                        f"Progress: {progress['completion_percentage']:.1f}%, "
                        f"Failed: {progress['failed_stories']}")
                        
            await asyncio.sleep(update_interval)

# CLI interface functions
async def run_full_generation(config_path: str = "config/generation_config.yaml"):
    """Run complete story generation process"""
    processor = BatchProcessor(config_path)
    return await processor.run_full_generation()
    
async def run_test(size: int = 5, config_path: str = "config/generation_config.yaml"):
    """Run a test batch"""
    processor = BatchProcessor(config_path)
    return await processor.run_test_batch(size)
    
async def retry_failed(config_path: str = "config/generation_config.yaml"):
    """Retry failed stories"""
    processor = BatchProcessor(config_path)
    return await processor.retry_failed_stories()