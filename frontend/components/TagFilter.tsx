'use client';

import { useEffect, useState } from 'react';
import { getAllTags } from '@/lib/api';

interface TagFilterProps {
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
}

export default function TagFilter({ selectedTags, onTagsChange }: TagFilterProps) {
  const [allTags, setAllTags] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAllTags()
      .then(setAllTags)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const toggleTag = (tag: string) => {
    if (selectedTags.includes(tag)) {
      onTagsChange(selectedTags.filter((t) => t !== tag));
    } else {
      onTagsChange([...selectedTags, tag]);
    }
  };

  const clearTags = () => {
    onTagsChange([]);
  };

  return (
    <div className="relative">
      <div className="flex items-center gap-2 flex-wrap">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
        >
          <span>Filter by Tags</span>
          {selectedTags.length > 0 && (
            <span className="px-2 py-0.5 bg-blue-600 text-white text-sm rounded-full">
              {selectedTags.length}
            </span>
          )}
        </button>

        {selectedTags.length > 0 && (
          <button
            onClick={clearTags}
            className="px-3 py-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Clear filters
          </button>
        )}
      </div>

      {selectedTags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {selectedTags.map((tag) => (
            <span
              key={tag}
              className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm flex items-center gap-2"
            >
              {tag}
              <button
                onClick={() => toggleTag(tag)}
                className="hover:text-blue-900"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {isOpen && (
        <div className="absolute z-10 mt-2 w-full max-w-md bg-white border border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500">Loading tags...</div>
          ) : allTags.length === 0 ? (
            <div className="p-4 text-center text-gray-500">No tags available</div>
          ) : (
            <div className="p-2">
              {allTags.map((tag) => (
                <label
                  key={tag}
                  className="flex items-center gap-2 px-3 py-2 hover:bg-gray-50 rounded cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedTags.includes(tag)}
                    onChange={() => toggleTag(tag)}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-gray-700">{tag}</span>
                </label>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
