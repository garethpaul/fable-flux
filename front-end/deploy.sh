#!/bin/bash

# Fable Flux Deployment Script for Vercel
echo "🚀 Deploying Fable Flux to Vercel..."

# Check if we're in the front-end directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the front-end directory"
    echo "   cd front-end && ./deploy.sh"
    exit 1
fi

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📝 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial Fable Flux deployment"
fi

# Build the project locally to check for errors
echo "🔨 Building project locally..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed! Please fix the errors before deploying."
    exit 1
fi

echo "✅ Build successful!"

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://vercel.com/dashboard"
echo "2. Find your project and click on it"
echo "3. Go to Settings > Environment Variables"
echo "4. Add: MODAL_API_KEY = your_actual_modal_api_key"
echo "5. Add: MODAL_API_URL = https://your-modal-endpoint.example.com/v1/chat/completions"
echo "6. Add MODAL_MODEL if your served model name differs from the default"
echo "7. Redeploy if needed"
echo ""
echo "🌐 Your app will be available at the URL shown above!"
