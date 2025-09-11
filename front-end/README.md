# Fable Flux - AI-Powered Bedtime Story Generator

A beautiful React/Next.js frontend application that generates personalized bedtime stories using advanced AI technology and the Fable Flux fine-tuned model.

## 🌟 Features

- **Interactive Landing Page**: Beautiful gradient design with clear call-to-action
- **Modal-Based Story Input**: Clean modal interface for entering story prompts
- **AI Story Generation**: Powered by GPT-5-Mini via Poe API
- **Story Display Page**: Beautifully formatted story presentation
- **Responsive Design**: Mobile-first design that works on all devices
- **Error Handling**: Comprehensive error states with user-friendly messages
- **Loading States**: Smooth loading indicators during story generation
- **Character Counter**: Real-time character count with 200 character limit

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Valid Poe API key

### Installation

1. **Navigate to the frontend directory:**

   ```bash
   cd front-end
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Configure environment variables:**

   You can set the POE_API_KEY in two ways:

   **Option 1: Using .env.local file (recommended for development):**

   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local` and add your Poe API key:

   ```env
   POE_API_KEY=your_actual_poe_api_key_here
   ```

   **Option 2: Using system environment variables (recommended for production):**

   ```bash
   export POE_API_KEY=your_actual_poe_api_key_here
   ```

   Note: System environment variables take precedence over .env.local settings.

4. **Start the development server:**

   ```bash
   npm run dev
   ```

5. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
front-end/
├── src/
│   ├── app/                     # Next.js App Router
│   │   ├── api/
│   │   │   └── chat/
│   │   │       └── completions/
│   │   │           └── route.ts # Poe API proxy endpoint
│   │   ├── story/
│   │   │   └── page.tsx        # Story display page
│   │   ├── layout.tsx          # Root layout with metadata
│   │   ├── page.tsx            # Landing page
│   │   └── globals.css         # Global styles
│   ├── components/             # Reusable React components
│   │   ├── StoryModal.tsx      # Story input modal
│   │   ├── LoadingSpinner.tsx  # Loading indicator
│   │   └── ErrorMessage.tsx    # Error display component
│   └── types/
│       └── story.ts            # TypeScript type definitions
├── .env.local                  # Environment variables
├── package.json               # Dependencies and scripts
├── tailwind.config.js         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── README.md                  # This file
```

## 🎨 User Flow

1. **Landing Page** (`/`)

   - User sees beautiful Fable Flux homepage
   - Clicks "Create Your Story" or "Learn More" button

2. **Story Input Modal**

   - Modal opens with text area for story prompt
   - Real-time character counter (0-200 characters)
   - Form validation ensures prompt is provided
   - "Generate Story" button becomes enabled when text is entered

3. **Story Generation**

   - Loading spinner displays "Creating your story..."
   - API call made to `/api/chat/completions`
   - Server proxies request to Poe API with GPT-5-Mini model

4. **Story Display** (`/story`)
   - Generated story displayed with beautiful formatting
   - Includes title, characters, setting, story content, and moral
   - Options to create another story or print current story

## 🔧 API Integration

### Poe API Proxy

The application includes a Next.js API route that safely proxies requests to the Poe API:

**Endpoint:** `POST /api/chat/completions`

**Request Body:**

```json
{
  "prompt": "a brave little car who loves to help other vehicles"
}
```

**Response Format:**

```json
{
  "title": "The Helpful Little Red Car",
  "characters": "Ruby the red car, broken-down truck, other vehicles",
  "setting": "Busy city street",
  "story": "Once upon a time...",
  "moral": "Helping others brings joy to everyone."
}
```

### Security Features

- **Server-side API Key**: Poe API key is stored securely server-side
- **Input Validation**: Prompt validation and sanitization
- **Error Handling**: Comprehensive error responses
- **Rate Limiting**: Configurable through Poe API settings

## 🎨 Design System

### Colors

- **Primary**: Blue (#2563eb)
- **Secondary**: Indigo (#4f46e5)
- **Success**: Green (#10b981)
- **Warning**: Amber (#f59e0b)
- **Error**: Red (#ef4444)

### Typography

- **Primary Font**: Geist Sans
- **Monospace**: Geist Mono

### Responsive Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🛠️ Development

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run ESLint
npm run lint
```

### Environment Variables

| Variable      | Description                           | Required |
| ------------- | ------------------------------------- | -------- |
| `POE_API_KEY` | Your Poe API key for story generation | Yes      |

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **New Pages**: Add to `src/app/` following App Router conventions
3. **API Routes**: Add to `src/app/api/`
4. **Types**: Add to `src/types/`

## 🐛 Troubleshooting

### Common Issues

1. **"Server configuration error"**

   - Ensure `POE_API_KEY` is set either as a system environment variable or in `.env.local`
   - System environment variables take precedence over .env.local
   - Restart the development server after adding environment variables
   - Check the terminal output for specific error messages about missing API key

2. **"Failed to generate story"**

   - Check that your Poe API key is valid
   - Verify you have sufficient API credits
   - Check network connectivity

3. **Stories not displaying**
   - Ensure localStorage is enabled in your browser
   - Check browser console for JavaScript errors

### Debug Mode

To enable detailed logging, check the browser console and terminal output when running in development mode.

## 📱 Mobile Support

The application is fully responsive and optimized for:

- **iOS Safari**
- **Android Chrome**
- **Mobile Firefox**
- **Progressive Web App** capabilities

## 🔒 Security Considerations

- API key is never exposed to client-side code
- Input sanitization prevents injection attacks
- CORS configured for secure API access
- Environment variables properly configured

## 🚀 Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Add `POE_API_KEY` environment variable in Vercel dashboard
3. Deploy automatically on push to main branch

### Environment Variables in Production

For production deployments, always use your platform's environment variable configuration:

- **Vercel**: Environment Variables section in project settings
- **Netlify**: Environment variables in site settings
- **Railway**: Environment variables in service settings
- **Docker**: Use `-e POE_API_KEY=your_key` or environment files

### Other Platforms

1. Build the application: `npm run build`
2. Set environment variables on your platform
3. Deploy the `.next` folder and `package.json`

## 📝 License

This project is part of the Synthetic Stories system.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review browser console and terminal logs
3. Verify your Poe API key and credits
4. Check network connectivity

---

**Made with ❤️ using Next.js, React, TypeScript, and Tailwind CSS**
