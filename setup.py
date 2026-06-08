#!/usr/bin/env python3
"""
Setup script for the Story Generation System
"""

import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create required directory structure"""
    directories = [
        'src',
        'data',
        'config',
        'logs',
        'output',
        'output/generated_stories',
        'scripts'
    ]
    
    print("Creating directory structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}/")

def create_init_files():
    """Create __init__.py files for Python packages"""
    init_files = [
        'src/__init__.py'
    ]
    
    print("Creating Python package files...")
    for init_file in init_files:
        Path(init_file).touch()
        print(f"  ✓ {init_file}")

def check_environment():
    """Check environment setup"""
    print("Checking environment...")
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("  ✗ Python 3.7+ required")
        return False
    else:
        print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check API key
    if os.getenv('POE_API_KEY'):
        print("  ✓ POE_API_KEY environment variable set")
    else:
        print("  ⚠ POE_API_KEY environment variable not set")
        print("    Set it with: export POE_API_KEY='your_poe_api_key_here'")
    
    return True

def create_example_env():
    """Create example environment file"""
    env_content = """# Fable Flux environment variables
# Copy this file to .env or export the values in your shell. Do not commit real secrets.

# Required for Python story generation
POE_API_KEY=your_poe_api_key_here

# Required for Hugging Face dataset uploads
HF_TOKEN=your_huggingface_token_here

# Required by the Next.js frontend API proxy. See front-end/.env.local.example.
MODAL_API_KEY=your_modal_api_key_here
MODAL_API_URL=https://your-modal-app.modal.run/v1/chat/completions
MODAL_MODEL=garethpaul/gpt-oss-20b-fableflux-mxfp4
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    print("  ✓ Created .env.example")

def create_requirements():
    """Create requirements.txt file"""
    requirements = """# Core dependencies
aiohttp>=3.8.0
aiofiles>=0.8.0
PyYAML>=6.0

# Optional dependencies for enhanced validation
textstat>=0.7.0
textblob>=0.17.0

# Hugging Face integration
huggingface_hub>=0.17.0
datasets>=2.14.0

# Development dependencies (optional)
pytest>=7.0.0
pytest-asyncio>=0.20.0
black>=22.0.0
"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("  ✓ Created requirements.txt")

def create_install_script():
    """Create installation script"""
    install_script = """#!/bin/bash
# Installation script for Story Generation System

echo "Setting up Story Generation System..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make scripts executable
chmod +x generate_stories.py
chmod +x setup.py

echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "2. Set required service keys:"
echo "   export POE_API_KEY='your_poe_api_key_here'"
echo "   export HF_TOKEN='your_huggingface_token_here'"
echo ""
echo "3. Run a test:"
echo "   python generate_stories.py --test"
echo ""
echo "4. Start full generation:"
echo "   python generate_stories.py --generate"
"""
    
    with open('install.sh', 'w') as f:
        f.write(install_script)
    
    # Make executable
    os.chmod('install.sh', 0o755)
    print("  ✓ Created install.sh")

def main():
    """Main setup function"""
    print("Story Generation System Setup")
    print("=" * 40)
    
    if not check_environment():
        sys.exit(1)
    
    create_directory_structure()
    create_init_files()
    create_requirements()
    create_example_env()
    create_install_script()
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set API keys: export POE_API_KEY='your_poe_api_key_here' HF_TOKEN='your_huggingface_token_here'")
    print("3. Run test: python generate_stories.py --test")
    print("4. Start generation: python generate_stories.py --generate")

if __name__ == '__main__':
    main()
