# Frontend Setup Guide

This document provides instructions for setting up and running the Next.js frontend application for the Reddit Job Posts project.

## Overview

The frontend is a modern Next.js 15 application with the following features:
- **Search functionality** - Search job posts by title and description
- **Tag-based filtering** - Filter jobs using multiple tags
- **Pagination** - Navigate through large sets of results
- **Job detail pages** - View full job information
- **Responsive design** - Works on all device sizes

## Quick Start

### 1. Navigate to the frontend directory

```bash
cd frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure environment variables

Create a `.env.local` file in the frontend directory:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Note: Make sure the API backend is running on the specified URL (default: http://localhost:8000)

### 4. Start the development server

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                        # Next.js App Router pages
│   ├── jobs/[id]/
│   │   └── page.tsx           # Individual job detail page
│   ├── layout.tsx             # Root layout with metadata
│   ├── page.tsx               # Home page with job list
│   └── globals.css            # Global styles
├── components/                 # React components
│   ├── JobCard.tsx            # Job card for list view
│   ├── Pagination.tsx         # Pagination controls
│   ├── SearchBar.tsx          # Search input
│   └── TagFilter.tsx          # Tag filter dropdown
├── lib/                       # Utilities and services
│   ├── api.ts                 # API client functions
│   └── types.ts               # TypeScript type definitions
├── public/                    # Static assets
├── .env.local                 # Environment variables (create this)
├── next.config.ts             # Next.js configuration
├── tailwind.config.ts         # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
├── package.json               # Dependencies and scripts
└── README.md                  # Frontend documentation
```

## Available Scripts

### Development
```bash
npm run dev
```
Starts the development server with hot-reload at http://localhost:3000

### Production Build
```bash
npm run build
```
Creates an optimized production build

### Start Production Server
```bash
npm start
```
Runs the production build (must run `npm run build` first)

### Linting
```bash
npm run lint
```
Runs ESLint to check for code quality issues

## API Endpoints Used

The frontend communicates with the following API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/job-posts` | GET | List jobs with filtering, search, and pagination |
| `/api/v1/job-posts/{id}` | GET | Get a specific job by ID |
| `/api/v1/tags` | GET | Get all available tags |

## Features in Detail

### Search
- Type in the search bar and press Enter or click the Search button
- Searches across job titles and descriptions
- Automatically resets to page 1 when searching

### Tag Filtering
- Click "Filter by Tags" to open the dropdown
- Select multiple tags to filter jobs (OR logic - shows jobs with any of the selected tags)
- Selected tags appear as chips below the filter button
- Click the X on a tag chip or uncheck in dropdown to remove it
- Use "Clear filters" to remove all tag filters at once

### Pagination
- Navigate between pages using Previous/Next buttons
- Click specific page numbers for direct navigation
- Shows ellipsis (...) for large page ranges
- Automatically updates URL for shareable links

### Job Details
- Click any job card to view full details
- Shows complete job description with formatting preserved
- Displays all associated tags
- Links to original Reddit post
- Back button returns to previous page with filters preserved

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` | Backend API base URL |

## Styling

The application uses **Tailwind CSS** for styling with:
- Responsive breakpoints for mobile, tablet, and desktop
- Consistent color scheme with blue accents
- Hover states and transitions for better UX
- Loading spinners and error states

## TypeScript

The project is fully typed with TypeScript:
- All API responses have type definitions
- Component props are strictly typed
- Type-safe state management
- Compile-time error checking

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Port 3000 already in use
```bash
# Find the process using port 3000
lsof -i :3000

# Kill it (replace PID with actual process ID)
kill -9 <PID>

# Or use a different port
PORT=3001 npm run dev
```

### API connection errors
- Verify the API backend is running: `curl http://localhost:8000/health`
- Check `.env.local` has the correct `NEXT_PUBLIC_API_URL`
- Ensure CORS is enabled on the API (already configured in the backend)

### Build errors
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Try building again
npm run build
```

## Deployment

### Vercel (Recommended)
1. Push your code to GitHub
2. Import project in Vercel dashboard
3. Add environment variable: `NEXT_PUBLIC_API_URL=<your-api-url>`
4. Deploy

### Docker
Create a `Dockerfile`:
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t reddit-jobs-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://api:8000 reddit-jobs-frontend
```

## Development Tips

1. **URL State Management**: The app uses URL query parameters for filters, making views shareable
2. **Lazy Loading**: Components load data client-side for better interactivity
3. **Error Handling**: All API calls include proper error handling and user feedback
4. **Accessibility**: Use semantic HTML and ARIA labels where appropriate
5. **Performance**: Images and fonts are optimized by Next.js automatically

## Contributing

When adding new features:
1. Add TypeScript types in `lib/types.ts`
2. Add API functions in `lib/api.ts`
3. Create reusable components in `components/`
4. Follow existing naming conventions
5. Test on multiple screen sizes
6. Run `npm run lint` before committing

## License

Part of the reddit-job-posts-web-scraping project.
