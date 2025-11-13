import { JobPost, JobPostListResponse, JobPostFilters, Stats } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      `API request failed: ${response.statusText}`,
      response.status,
      errorData.detail
    );
  }

  return response.json();
}

export async function getJobPosts(filters: JobPostFilters = {}): Promise<JobPostListResponse> {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value));
    }
  });

  const queryString = params.toString();
  const endpoint = `/api/v1/job-posts${queryString ? `?${queryString}` : ''}`;

  return fetchApi<JobPostListResponse>(endpoint);
}

export async function getJobPost(id: number): Promise<JobPost> {
  return fetchApi<JobPost>(`/api/v1/job-posts/${id}`);
}

export async function getAllTags(): Promise<string[]> {
  return fetchApi<string[]>('/api/v1/tags');
}

export async function getStats(): Promise<Stats> {
  return fetchApi<Stats>('/api/v1/stats');
}
