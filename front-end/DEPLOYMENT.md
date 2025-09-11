# Deploying Fable Flux to Vercel

This guide will help you deploy your Fable Flux application to Vercel with a custom project URL like `fableflux.vercel.app`.

## 🚀 Quick Deployment Steps

### 1. Prerequisites

- GitHub account
- Vercel account (free at [vercel.com](https://vercel.com))
- Your POE_API_KEY ready

### 2. Prepare Your Repository

First, ensure your code is in a GitHub repository:

```bash
# Initialize git if not already done
cd synthetic-stories
git init

# Add all files
git add .

# Commit your changes
git commit -m "Initial Fable Flux application"

# Create a new repository on GitHub and push
git remote add origin https://github.com/yourusername/fable-flux.git
git branch -M main
git push -u origin main
```

### 3. Deploy to Vercel

#### Option A: Using Vercel Dashboard (Recommended)

1. **Go to [vercel.com](https://vercel.com)** and sign in with GitHub
2. **Click "New Project"**
3. **Import your repository** (synthetic-stories or fable-flux)
4. **Configure the project:**

   - **Project Name**: `fableflux` (this will create fableflux.vercel.app)
   - **Root Directory**: `front-end` (important!)
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)

5. **Add Environment Variable:**

   - Click "Environment Variables"
   - Add: `POE_API_KEY` = `your_actual_poe_api_key_here`
   - Make sure it's set for Production, Preview, and Development

6. **Click "Deploy"**

#### Option B: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to front-end directory
cd front-end

# Deploy
vercel

# Follow the prompts:
# ? Set up and deploy "front-end"? [Y/n] y
# ? Which scope do you want to deploy to? [your-username]
# ? Link to existing project? [y/N] n
# ? What's your project's name? fableflux
# ? In which directory is your code located? ./
```

### 4. Configure Custom Domain (Optional)

If you want `fableflux.vercel.app` specifically:

1. **In Vercel Dashboard:**
   - Go to your project settings
   - Click "Domains"
   - Add `fableflux.vercel.app` as a custom domain
   - If the name is taken, try variations like:
     - `fableflux-ai.vercel.app`
     - `fableflux-stories.vercel.app`
     - `my-fableflux.vercel.app`

### 5. Set Environment Variables

In your Vercel project dashboard:

1. **Go to Settings > Environment Variables**
2. **Add the following:**

| Key           | Value                        | Environments                     |
| ------------- | ---------------------------- | -------------------------------- |
| `POE_API_KEY` | your_actual_poe_api_key_here | Production, Preview, Development |

3. **Redeploy** after adding environment variables

## 🔧 Vercel Configuration File (Optional)

Create `front-end/vercel.json` for advanced configuration:

```json
{
  "name": "fableflux",
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "POE_API_KEY": "@poe_api_key"
  },
  "regions": ["iad1"]
}
```

## 📁 Project Structure for Deployment

Make sure your project structure looks like this:

```
synthetic-stories/
├── front-end/                 # This is your Vercel root directory
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   └── .env.local (not deployed)
└── other-files/
```

## 🚨 Important Notes

### Environment Variables

- **Never commit `.env.local`** to Git
- **Always set POE_API_KEY** in Vercel dashboard
- **Use the same key** for all environments (Production, Preview, Development)

### Build Configuration

- **Root Directory**: Must be set to `front-end`
- **Build Command**: `npm run build` (default)
- **Node.js Version**: 18.x (recommended)

### Domain Availability

- `fableflux.vercel.app` might be taken
- Try variations: `fableflux-ai`, `fableflux-stories`, `my-fableflux`
- You can always change the domain later

## 🎯 Step-by-Step Checklist

- [ ] Code pushed to GitHub repository
- [ ] Vercel account connected to GitHub
- [ ] New project created with correct settings:
  - [ ] Root directory: `front-end`
  - [ ] Project name: `fableflux` (or variant)
  - [ ] Framework: Next.js
- [ ] Environment variable added:
  - [ ] `POE_API_KEY` set in Vercel dashboard
- [ ] First deployment successful
- [ ] Custom domain configured (if desired)
- [ ] Application tested on production URL

## 🔍 Troubleshooting

### Build Fails

```bash
# Check build locally first
cd front-end
npm run build
```

### Environment Variable Issues

- Ensure `POE_API_KEY` is set in Vercel dashboard
- Redeploy after adding environment variables
- Check spelling and case sensitivity

### Domain Already Taken

- Try variations: `fableflux-ai`, `fableflux-stories`
- Use your username: `username-fableflux`
- Add year: `fableflux-2024`

## 🚀 Alternative Deployment URLs

If `fableflux.vercel.app` is unavailable, consider:

- `fableflux-ai.vercel.app`
- `fableflux-stories.vercel.app`
- `fableflux-app.vercel.app`
- `my-fableflux.vercel.app`
- `awesome-fableflux.vercel.app`

## 📞 Support

If you encounter issues:

1. Check Vercel's deployment logs
2. Verify environment variables are set
3. Test build locally: `npm run build`
4. Check Vercel documentation: [vercel.com/docs](https://vercel.com/docs)

---

**Your Fable Flux app will be live at: `https://your-project-name.vercel.app`**
