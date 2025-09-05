#!/usr/bin/env python3
"""
Main script for story generation
Provides command-line interface for the story generation system
"""

import asyncio
import argparse
import os
import sys
import logging
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from batch_processor import BatchProcessor, run_full_generation, run_test, retry_failed

def setup_environment():
    """
    Setup environment and check requirements
    """
    # Check for required environment variables
    if not os.getenv('POE_API_KEY'):
        print("ERROR: POE_API_KEY environment variable must be set")
        print("Example: export POE_API_KEY='your_api_key_here'")
        sys.exit(1)
        
    # Create required directories
    directories = ['logs', 'output', 'output/generated_stories']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("        CHILDREN'S STORY GENERATOR")
    print("        Extending 1,500 stories to 10,000")
    print("=" * 60)
    print()

async def main():
    parser = argparse.ArgumentParser(
        description="Generate children's educational stories using Poe API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_stories.py --test                    # Run test generation (5 stories)
  python generate_stories.py --test --size 10         # Run test with 10 stories
  python generate_stories.py --generate               # Run full generation (1501-10000)
  python generate_stories.py --retry                  # Retry failed stories
  python generate_stories.py --stats                  # Show current statistics
  python generate_stories.py --batch 1501 1600       # Generate specific range
        """
    )
    
    # Action group - exactly one required
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--test', action='store_true',
                             help='Run test generation with small batch')
    action_group.add_argument('--generate', action='store_true',
                             help='Run full story generation (1501-10000)')
    action_group.add_argument('--retry', action='store_true',
                             help='Retry previously failed stories')
    action_group.add_argument('--stats', action='store_true',
                             help='Show current generation statistics')
    action_group.add_argument('--batch', nargs=2, type=int, metavar=('START', 'END'),
                             help='Generate specific range of stories')
    
    # Optional arguments
    parser.add_argument('--size', type=int, default=5,
                       help='Number of stories for test generation (default: 5)')
    parser.add_argument('--config', default='config/generation_config.yaml',
                       help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Reduce logging output')
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        log_level = logging.DEBUG
    elif args.quiet:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO
        
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/generation.log')
        ]
    )
    
    print_banner()
    setup_environment()
    
    try:
        if args.test:
            print(f"Running test generation with {args.size} stories...")
            results = await run_test(args.size, args.config)
            print(f"\nTest Results:")
            print(f"  Successful: {results['successful']}")
            print(f"  Failed: {results['failed']}")
            if results['failed'] > 0:
                print(f"  Failed IDs: {results['failed_ids']}")
                
        elif args.generate:
            print("Starting full story generation (1501-10000)...")
            print("This will take several hours. Press Ctrl+C to stop gracefully.")
            results = await run_full_generation(args.config)
            print(f"\nFinal Results:")
            print(f"  Total Completed: {results['total_completed']}")
            print(f"  Total Failed: {results['total_failed']}")
            print(f"  Success Rate: {results['total_completed']/(results['total_completed']+results['total_failed'])*100:.1f}%")
            
        elif args.retry:
            print("Retrying previously failed stories...")
            results = await retry_failed(args.config)
            print(f"\nRetry Results:")
            print(f"  Stories Retried: {results['total_retried']}")
            print(f"  Now Successful: {results['successful']}")
            print(f"  Still Failed: {results['still_failed']}")
            
        elif args.stats:
            processor = BatchProcessor(args.config)
            stats = processor.get_current_stats()
            
            print("Current Generation Statistics:")
            print("=" * 40)
            progress = stats['progress']
            print(f"Completed Stories: {progress['completed_stories']}")
            print(f"Target Total: {progress['total_target']}")
            print(f"Progress: {progress['completion_percentage']:.1f}%")
            print(f"Failed Stories: {progress['failed_stories']}")
            print(f"Last Story ID: {progress['last_story_id']}")
            
            if 'diversity' in stats:
                div = stats['diversity']
                print(f"\nDiversity Stats:")
                print(f"  Characters - Min/Max usage: {div['character_usage']['min']}/{div['character_usage']['max']}")
                print(f"  Settings - Min/Max usage: {div['setting_usage']['min']}/{div['setting_usage']['max']}")
                print(f"  Story Types: {div['story_types']}")
                print(f"  Unique Tag Combinations: {div['unique_tag_combinations']}")
                
        elif args.batch:
            start_id, end_id = args.batch
            print(f"Generating stories {start_id} to {end_id}...")
            processor = BatchProcessor(args.config)
            results = await processor.generator.generate_story_batch(start_id, end_id)
            print(f"\nBatch Results:")
            print(f"  Successful: {results['successful']}")
            print(f"  Failed: {results['failed']}")
            
    except KeyboardInterrupt:
        print("\nGeneration interrupted by user. Progress has been saved.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        logging.error(f"Generation failed: {e}")
        sys.exit(1)
        
    print("\nGeneration completed successfully!")

if __name__ == '__main__':
    asyncio.run(main())