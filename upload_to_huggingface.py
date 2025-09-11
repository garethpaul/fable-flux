#!/usr/bin/env python3
"""
Upload Children's Stories Dataset to Hugging Face Hub

This script provides a simple interface to upload your children's stories
to Hugging Face Hub as a dataset in JSONL format.

Usage:
    python upload_to_huggingface.py --repo-name "your-username/children-stories-dataset"

Environment Variables:
    HF_TOKEN: Your Hugging Face access token
"""

import os
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from huggingface_uploader import HuggingFaceUploader
except ImportError as e:
    print(f"❌ Error importing uploader: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip install huggingface_hub datasets")
    sys.exit(1)


def main():
    """Main upload function with user-friendly interface"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 Children's Stories Dataset Uploader")
    print("=" * 50)
    
    # Get Hugging Face token
    token = os.getenv('HF_TOKEN')
    if not token:
        print("❌ Hugging Face token not found!")
        print("Please set your HF_TOKEN environment variable:")
        print("export HF_TOKEN='your_token_here'")
        print("\nYou can get a token from: https://huggingface.co/settings/tokens")
        return False
    
    # Get repository name
    repo_name = input("\n📝 Enter repository name (e.g., 'username/children-stories-dataset'): ").strip()
    if not repo_name:
        print("❌ Repository name is required!")
        return False
    
    # Validate repo name format
    if '/' not in repo_name:
        print("❌ Repository name should be in format 'username/dataset-name'")
        return False
    
    # Ask about privacy
    make_private = input("\n🔒 Make repository private? (y/N): ").strip().lower() == 'y'
    
    # Ask about what to include
    print("\n📚 What stories to include:")
    print("1. All stories (existing + generated)")
    print("2. Only existing stories")
    print("3. Only generated stories")
    
    choice = input("Choose option (1-3) [1]: ").strip() or "1"
    
    include_existing = choice in ["1", "2"]
    include_generated = choice in ["1", "3"]
    
    if choice not in ["1", "2", "3"]:
        print("❌ Invalid choice!")
        return False
    
    # Show summary
    print(f"\n📋 Upload Summary:")
    print(f"Repository: {repo_name}")
    print(f"Private: {'Yes' if make_private else 'No'}")
    print(f"Include existing stories: {'Yes' if include_existing else 'No'}")
    print(f"Include generated stories: {'Yes' if include_generated else 'No'}")
    
    confirm = input("\n✅ Proceed with upload? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Upload cancelled.")
        return False
    
    try:
        # Create uploader
        print("\n🔧 Initializing uploader...")
        uploader = HuggingFaceUploader(token=token)
        
        # Upload dataset
        print("🚀 Starting upload...")
        result = uploader.create_and_upload_dataset(
            stories_dir=Path.cwd(),
            repo_name=repo_name,
            private=make_private,
            include_existing=include_existing,
            include_generated=include_generated
        )
        
        # Show results
        print("\n🎉 Upload completed successfully!")
        print("=" * 50)
        print(f"📁 Repository URL: {result['repo_url']}")
        print(f"📄 Local JSONL file: {result['jsonl_file']}")
        print(f"📚 Total stories uploaded: {result['num_stories']}")
        print(f"⏰ Upload time: {result['upload_time']}")
        
        print(f"\n🔗 View your dataset at:")
        print(f"https://huggingface.co/datasets/{repo_name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        logging.error(f"Upload error: {e}", exc_info=True)
        return False


def quick_upload(repo_name: str, 
                private: bool = False,
                include_existing: bool = True,
                include_generated: bool = True):
    """Quick upload function for programmatic use"""
    
    token = os.getenv('HF_TOKEN')
    if not token:
        raise ValueError("HF_TOKEN environment variable not set")
    
    uploader = HuggingFaceUploader(token=token)
    return uploader.create_and_upload_dataset(
        stories_dir=Path.cwd(),
        repo_name=repo_name,
        private=private,
        include_existing=include_existing,
        include_generated=include_generated
    )


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload children's stories to Hugging Face Hub")
    parser.add_argument("--repo-name", help="Repository name (e.g., 'username/dataset-name')")
    parser.add_argument("--private", action="store_true", help="Make repository private")
    parser.add_argument("--existing-only", action="store_true", help="Include only existing stories")
    parser.add_argument("--generated-only", action="store_true", help="Include only generated stories")
    parser.add_argument("--quick", action="store_true", help="Skip interactive prompts")
    
    args = parser.parse_args()
    
    if args.quick and args.repo_name:
        # Quick mode - no prompts
        try:
            include_existing = not args.generated_only
            include_generated = not args.existing_only
            
            result = quick_upload(
                repo_name=args.repo_name,
                private=args.private,
                include_existing=include_existing,
                include_generated=include_generated
            )
            
            print(f"✅ Quick upload successful: {result['repo_url']}")
            print(f"📚 {result['num_stories']} stories uploaded")
            
        except Exception as e:
            print(f"❌ Quick upload failed: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        success = main()
        sys.exit(0 if success else 1)