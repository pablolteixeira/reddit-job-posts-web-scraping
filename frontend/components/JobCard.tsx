'use client';

import Link from 'next/link';
import { JobPost } from '@/lib/types';

interface JobCardProps {
  job: JobPost;
}

export default function JobCard({ job }: JobCardProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <Link href={`/jobs/${job.id}`}>
      <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <h2 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
          {job.cleaned_title || 'Untitled Job Post'}
        </h2>

        <p className="text-gray-600 mb-4 line-clamp-3">
          {job.cleaned_text || 'No description available'}
        </p>

        <div className="flex items-center justify-between">
          <div className="flex flex-wrap gap-2">
            {job.tags && job.tags.length > 0 ? (
              job.tags.slice(0, 3).map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                >
                  {tag}
                </span>
              ))
            ) : (
              <span className="text-gray-400 text-sm">No tags</span>
            )}
            {job.tags && job.tags.length > 3 && (
              <span className="text-gray-500 text-xs self-center">
                +{job.tags.length - 3} more
              </span>
            )}
          </div>

          <span className="text-sm text-gray-500">
            {formatDate(job.created_utc)}
          </span>
        </div>
      </div>
    </Link>
  );
}
