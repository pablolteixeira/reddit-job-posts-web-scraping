'use client';

import { Suspense, useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { getJobPosts } from '@/lib/api';
import { JobPostListResponse } from '@/lib/types';
import SearchBar from '@/components/SearchBar';
import TagFilter from '@/components/TagFilter';
import JobCard from '@/components/JobCard';
import Pagination from '@/components/Pagination';

function JobsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [jobsData, setJobsData] = useState<JobPostListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get filters from URL params
  const currentPage = Number(searchParams.get('page')) || 1;
  const searchQuery = searchParams.get('search') || '';
  const selectedTagsParam = searchParams.get('tags') || '';
  const selectedTags = selectedTagsParam ? selectedTagsParam.split(',') : [];

  useEffect(() => {
    const fetchJobs = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getJobPosts({
          page: currentPage,
          page_size: 20,
          search: searchQuery || undefined,
          tags: selectedTagsParam || undefined,
          has_cleaned_data: true,
          sort_by: 'created_utc',
          sort_order: 'desc',
        });
        setJobsData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [currentPage, searchQuery, selectedTagsParam]);

  const updateUrlParams = (updates: Record<string, string | null>) => {
    const params = new URLSearchParams(searchParams.toString());

    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });

    // Reset to page 1 when filters change
    if ('search' in updates || 'tags' in updates) {
      params.set('page', '1');
    }

    router.push(`/?${params.toString()}`);
  };

  const handleSearch = (query: string) => {
    updateUrlParams({ search: query || null });
  };

  const handleTagsChange = (tags: string[]) => {
    updateUrlParams({ tags: tags.length > 0 ? tags.join(',') : null });
  };

  const handlePageChange = (page: number) => {
    updateUrlParams({ page: String(page) });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Reddit Job Posts
          </h1>
          <p className="text-gray-600">
            Browse and search job opportunities from Reddit
          </p>
        </div>

        {/* Search and Filters */}
        <div className="mb-6 space-y-4">
          <SearchBar initialValue={searchQuery} onSearch={handleSearch} />
          <TagFilter selectedTags={selectedTags} onTagsChange={handleTagsChange} />
        </div>

        {/* Results */}
        {loading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        ) : jobsData && jobsData.data.length > 0 ? (
          <>
            <div className="mb-4 text-gray-600">
              Found {jobsData.total} job{jobsData.total !== 1 ? 's' : ''}
            </div>

            <div className="grid gap-4 mb-8">
              {jobsData.data.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>

            <Pagination
              currentPage={jobsData.page}
              totalPages={jobsData.total_pages}
              onPageChange={handlePageChange}
            />
          </>
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-500 text-lg">No jobs found</p>
            <p className="text-gray-400 mt-2">Try adjusting your search or filters</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Home() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 flex justify-center items-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    }>
      <JobsContent />
    </Suspense>
  );
}
