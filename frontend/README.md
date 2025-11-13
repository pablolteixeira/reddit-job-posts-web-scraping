# Reddit Job Posts Frontend

A Next.js frontend application for browsing and searching job posts scraped from Reddit.

## Features

- **Search**: Full-text search across job titles and descriptions
- **Tag Filtering**: Filter jobs by multiple tags with an intuitive dropdown interface
- **Pagination**: Browse through large result sets with easy navigation
- **Job Details**: View complete job information on dedicated detail pages
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Real-time Updates**: URL-based state management for shareable filtered views

## Tech Stack

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React Hooks**: Modern state management

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Running API backend (see `/api` directory)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure the API URL:
Create a `.env.local` file in the root directory:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── jobs/[id]/
│   │   └── page.tsx          # Job detail page
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Home page (jobs list)
│   └── globals.css            # Global styles
├── components/
│   ├── JobCard.tsx            # Job list item component
│   ├── Pagination.tsx         # Pagination controls
│   ├── SearchBar.tsx          # Search input component
│   └── TagFilter.tsx          # Tag filtering component
├── lib/
│   ├── api.ts                 # API service layer
│   └── types.ts               # TypeScript type definitions
└── .env.local                 # Environment variables
```

## API Integration

The frontend communicates with the FastAPI backend through the following endpoints:

- `GET /api/v1/job-posts` - List jobs with filtering and pagination
- `GET /api/v1/job-posts/{id}` - Get job details
- `GET /api/v1/tags` - Get all available tags

See `/lib/api.ts` for the complete API service implementation.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000` |

## Development

### Code Quality

The project uses:
- ESLint for code linting
- TypeScript for type checking
- Prettier-compatible formatting

Run linting:
```bash
npm run lint
```

### Component Development

All components are TypeScript-based with proper type definitions. The UI uses Tailwind CSS for styling with a focus on:
- Responsive design patterns
- Accessible markup
- Loading and error states
- User feedback

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new) from the creators of Next.js.

Check out the [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## License

This project is part of the reddit-job-posts-web-scraping repository.
