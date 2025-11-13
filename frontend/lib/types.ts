export interface JobPost {
  id: number;
  cleaned_title: string | null;
  cleaned_text: string | null;
  tags: string[] | null;
  created_utc: string;
  url: string | null;
}

export interface JobPostListResponse {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  data: JobPost[];
}

export interface JobPostFilters {
  page?: number;
  page_size?: number;
  search?: string;
  tags?: string;
  from_date?: string;
  to_date?: string;
  has_cleaned_data?: boolean;
  sort_by?: 'created_utc' | 'processed_at' | 'score';
  sort_order?: 'asc' | 'desc';
}

export interface Stats {
  total_posts: number;
  posts_with_cleaned_data: number;
  posts_without_cleaned_data: number;
  oldest_post_date: string | null;
  newest_post_date: string | null;
}
