#!/bin/bash
# Installation script for Story Generation System

echo "Setting up Story Generation System..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv story_generator
source story_generator/bin/activate  # On Windows: story_generator\Scripts\activate

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
echo "   source story_generator/bin/activate"
echo ""
echo "2. Set your API key:"
echo "   export POE_API_KEY='your_api_key_here'"
echo ""
echo "3. Run a test:"
echo "   python generate_stories.py --test"
echo ""
echo "4. Start full generation:"
echo "   python generate_stories.py --generate"
