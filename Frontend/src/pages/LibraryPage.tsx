import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Search, BookOpen } from 'lucide-react'
import { Button, Card, LoadingSpinner } from '@/components/ui'
import { StoryCard } from '@/components/story'
import { storyApi } from '@/api'
import { Link } from 'react-router-dom'
import type { Story, PaginatedResponse } from '@/types'

export default function LibraryPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const pageSize = 9

  // Fetch stories (use caching to reduce repeated loads)
  const { data, isLoading } = useQuery<PaginatedResponse<Story>>({
    queryKey: ['stories', page, pageSize],
    queryFn: () => storyApi.getStories(page, pageSize),
    placeholderData: (previousData) => previousData,
    staleTime: 1000 * 30, // 30s
    gcTime: 1000 * 60 * 5, // 5 minutes
    retry: 1,
  })

  // Delete story mutation  
  const deleteMutation = useMutation({
    mutationFn: storyApi.deleteStory,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['stories'] })
      toast.success('Story deleted')
    },
    onError: () => {
      toast.error('Failed to delete story')
    },
  })

  // Filter stories by search query
  const filteredStories = data?.items?.filter((story: Story) => 
    searchQuery === '' || 
    story.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    story.genre.toLowerCase().includes(searchQuery.toLowerCase())
  ) || []

  return (
    <div className="min-h-screen py-8 md:py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div 
          className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div>
            <h1 className="text-3xl font-bold text-white">Story Library</h1>
            <p className="text-gray-400 mt-1">
              {data?.total || 0} stories in your collection
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search stories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 rounded-lg bg-story-muted/50 border border-story-border text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-story-accent/50 focus:border-story-accent w-64"
              />
            </div>
            <Link to="/create">
              <Button>New Story</Button>
            </Link>
          </div>
        </motion.div>

        {/* Stories Grid */}
        {isLoading ? (
          <div className="flex justify-center py-20">
            <LoadingSpinner size="lg" text="Loading your stories..." />
          </div>
        ) : filteredStories.length > 0 ? (
          <>
            <motion.div 
              className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              {filteredStories.map((story: Story, index: number) => (
                <motion.div
                  key={story.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <StoryCard 
                    story={story} 
                    onDelete={(id) => deleteMutation.mutate(id)}
                  />
                </motion.div>
              ))}
            </motion.div>

            {/* Pagination */}
            {data && data.pages > 1 && (
              <motion.div 
                className="flex items-center justify-center gap-4 mt-12"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Button
                  variant="secondary"
                  disabled={page === 1}
                  onClick={() => setPage(p => p - 1)}
                >
                  Previous
                </Button>
                <span className="text-gray-400">
                  Page {page} of {data.pages}
                </span>
                <Button
                  variant="secondary"
                  disabled={page === data.pages}
                  onClick={() => setPage(p => p + 1)}
                >
                  Next
                </Button>
              </motion.div>
            )}
          </>
        ) : (
          <Card className="text-center py-16">
            <BookOpen className="w-16 h-16 text-gray-500 mx-auto mb-6" />
            <h2 className="text-xl font-semibold text-white mb-2">
              {searchQuery ? 'No stories found' : 'Your library is empty'}
            </h2>
            <p className="text-gray-400 mb-8">
              {searchQuery 
                ? 'Try a different search term'
                : 'Create your first interactive adventure!'
              }
            </p>
            {!searchQuery && (
              <Link to="/create">
                <Button size="lg">Create Your First Story</Button>
              </Link>
            )}
          </Card>
        )}
      </div>
    </div>
  )
}
