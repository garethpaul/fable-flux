#!/bin/bash
# Installation script for Story Generation System

echo "Setting up Story Generation System..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

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
