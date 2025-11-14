# LB Marketing UI

Marketing dashboard UI for scheduling and publishing social media posts.

## Features

- 📝 Create and schedule posts for multiple platforms (Twitter/X, Facebook, Instagram, LinkedIn, YouTube)
- ⏰ Schedule posts for future publishing
- 🔗 OAuth integration for social media platforms
- 📊 View and manage scheduled posts
- 🚀 Publish all due posts with one click

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running (see `../lb_marketing_api/README.md`)

### Development

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open in browser**:
   Navigate to `http://localhost:5173`

The dev server uses a proxy to forward API requests to `http://localhost:8000` (your backend).

### Production Build

1. **Set environment variable** (optional for development):
   ```bash
   # Create .env file
   VITE_API_URL=https://api.yourdomain.com
   ```

2. **Build for production**:
   ```bash
   npm run build
   ```

3. **Preview production build**:
   ```bash
   npm run preview
   ```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `VITE_API_URL` | Backend API URL (e.g., `https://api.yourdomain.com`) | Production only |

**Note**: In development, leave `VITE_API_URL` empty to use the Vite proxy.

## Project Structure

```
src/
├── components/       # UI components (shadcn/ui)
├── lib/
│   ├── api.ts      # API utility functions
│   └── utils.ts    # Utility functions
├── simpleUI.tsx    # Main dashboard component
└── main.tsx        # Application entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions for:
- Vercel
- Netlify
- Azure Static Web Apps
- Manual deployment

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI component library
- **Lucide React** - Icons
